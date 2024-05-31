from typing import Dict
from pydantic import BaseModel

class GeneratePipeline(BaseModel):
    dataset_name: str
    problem_type: str
    target_column: str