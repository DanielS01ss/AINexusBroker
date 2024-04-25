from typing import List
from typing import Any
from pydantic import BaseModel
from typing import List

class UploadMetadata(BaseModel):
    user_email: str
    file_name: str
    tags: List[str]
    authors: List[str]
    publish: str
    description: str
