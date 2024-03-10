from typing import List
from typing import Dict
from pydantic import BaseModel
from typing import Any

class ModelDetailsRequest(BaseModel):
    email: str