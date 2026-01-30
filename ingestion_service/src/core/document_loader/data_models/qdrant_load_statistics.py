from typing import List
from pydantic import BaseModel


class LoadStatisticModel(BaseModel):
    total_chunks: int
    successful: int
    failed: int
    errors: List[str]