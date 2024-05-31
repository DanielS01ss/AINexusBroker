from typing import Dict
from pydantic import BaseModel

class GenerateKey(BaseModel):
    user_email: str
   