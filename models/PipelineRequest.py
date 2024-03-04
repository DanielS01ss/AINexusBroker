from typing import List

from pydantic import BaseModel


class PipelineRequest(BaseModel):
    dataset_name: str
    operations: List

