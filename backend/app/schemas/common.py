"""Envelopes shared by several endpoints."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    code: str


class Message(BaseModel):
    message: str
