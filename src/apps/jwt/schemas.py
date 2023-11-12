from pydantic import BaseModel


class AccessTokenOutputSchema(BaseModel):
    access_token: str
    

class ConfirmationTokenSchema(BaseModel):
    token: str
