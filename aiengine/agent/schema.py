from pydantic import BaseModel
from typing import List
class SearchTranslatedQueries(BaseModel):
    """Data model for a query."""
    Output: List[str]
