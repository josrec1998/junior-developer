from pydantic import BaseModel


class Source(BaseModel):
    id: str
    title: str
    source: str


class Source(BaseModel):
    id: str
    title: str
    source: str
    favicon: str | None = None
