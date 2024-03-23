from typing import Dict
from pydantic import BaseModel

class LogsRequest(BaseModel):
    email: str
    date: str
    logs: str