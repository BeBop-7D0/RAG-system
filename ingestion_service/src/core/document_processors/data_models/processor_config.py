from pydantic import BaseModel


class ProcessorConfig(BaseModel):
    min_paragraphs_len: int
    min_len_for_join: int
    min_len_for_split: int
    max_len_for_chunk: int