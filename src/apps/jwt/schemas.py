from pydantic import BaseModel


class AccessTokenOutputSchema(BaseModel):
    access_token: str
