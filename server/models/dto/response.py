from pydantic import BaseModel


class Response(BaseModel):
    status: int
    message: str | None

    @classmethod
    def success(cls, message: str | None = None):
        return cls(status=200, message=message)
