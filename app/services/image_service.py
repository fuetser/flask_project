from typing import NamedTuple


class RawImage(NamedTuple):
    image_bytes: bytes
    mimetype: str

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
