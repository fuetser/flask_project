from base64 import b64encode
from io import BytesIO
from dataclasses import dataclass

from PIL import Image
from werkzeug.datastructures import FileStorage

from app import exceptions


@dataclass
class RawImage:
    image_bytes: bytes
    mimetype: str

    @property
    def b64string(self):
        return b64encode(self.image_bytes).decode("u8")

    @property
    def extension(self):
        return self.mimetype.split("/")[-1]

    @classmethod
    def from_wtf_file(cls, wtf_file: FileStorage):
        image_bytes = convert_wtf_file_to_bytes(wtf_file)
        mimetype = get_mimetype_from_wtf_file(wtf_file)
        return cls(image_bytes, mimetype)

    def raise_for_image_validity(self):
        try:
            with BytesIO() as buffer:
                buffer.write(self.image_bytes)
                image = Image.open(buffer)
        except Exception as e:
            raise exceptions.ImageError(str(e)) from e

    def crop_to_64square(self):
        with BytesIO() as buffer, BytesIO() as dest:
            buffer.write(self.image_bytes)
            image = Image.open(buffer)

            min_side, max_side = sorted(image.size)
            side = 64 * max_side / min_side

            image.thumbnail((side, side))
            crop_to_square(image).save(dest, format=self.extension)
            self.image_bytes = dest.getvalue()


def convert_wtf_file_to_bytes(wtf_file: FileStorage):
    with BytesIO() as buffer:
        wtf_file.save(buffer)
        return buffer.getvalue()


def get_mimetype_from_wtf_file(wtf_file: FileStorage):
    return wtf_file.mimetype


def crop_to_square(image: Image) -> Image:
    width, height = image.size
    if width > height:
        x0 = (width - height) // 2
        y0 = 0
        x1 = (width + height) // 2
        y1 = height
    else:
        x0 = 0
        y0 = (height - width) // 2
        x1 = width
        y1 = (height + width) // 2
    return image.crop((x0, y0, x1, y1))
