from typing import List
from typing import Dict
from pydantic import BaseModel


class OperationRequest(BaseModel):
    dataset_name: str
    operation: Dict