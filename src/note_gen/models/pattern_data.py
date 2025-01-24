from pydantic import BaseModel, Field
from typing import List, Union

class NotePatternData(BaseModel):
    values: List[Union[int, List[Union[int, List[int]]]]]
    
    class Config:
        schema_extra = {
            "example": {
                "values": [[1, 2], [3, 4]]
            }
        }
