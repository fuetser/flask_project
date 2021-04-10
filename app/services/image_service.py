from typing import NamedTuple


class RawImage(NamedTuple):
    image_bytes: bytes
    mimetype: str

    @classmethod
    def from_wtf_file(cls, wtf_file):
        image_bytes = convert_wtf_file_to_bytes(wtf_file)
        mimetype = get_mimetype_from_wtf_file(wtf_file)
        return cls(image_bytes, mimetype)

    def raise_for_image_validity(self):
        raise NotImplementedError


class RawPostImage(RawImage):
    def raise_for_image_validity(self):
        ...


class RawGroupLogo(RawImage):
    def raise_for_image_validity(self):
        ...


class RawUserAvatar(RawImage):
    def raise_for_image_validity(self):
        ...
