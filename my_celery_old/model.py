from enum import IntEnum

from pydantic import BaseModel


class TransParam(BaseModel):
    src: str
    tpl: str
    out: str


class TransRes(IntEnum):
    ok = 0
    file_format_err = -1
    no_face = -2
    image_error = -3
    transform_error = -4
