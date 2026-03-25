from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    
# In a real app, you'd have a UserInDB model with the hashed_password
class UserInDB(User):
    hashed_password: str