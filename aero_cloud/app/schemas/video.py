from typing import Literal

from pydantic import BaseModel


class WebRtcOffer(BaseModel):
    sdp: str
    type: Literal["offer"]


class WebRtcAnswer(BaseModel):
    sdp: str
    type: Literal["answer"]
