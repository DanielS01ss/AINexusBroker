from typing import List

from pydantic import BaseModel


class PipelineSave(BaseModel):
    user_email: str
    pipeline_name: str
    pipeline_data: str
