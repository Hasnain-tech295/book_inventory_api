from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

# --- All Pydantic model in one place - good habit from day 1 ---

# --- Request Model: what the client sends to the server when creating a new book ---
class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100, description="Book Title")
    author: str = Field(min_length=1, max_length=100, description="Author full name")
    year: int = Field(gt=0, le=2100, description="Year of publication")
    isbn: Optional[str] = Field(default=None, description="Book ISBN (Optional)")

    # Custom validator: if ISBN is provided, it must be 13 digits long
    @field_validator("isbn")
    @classmethod
    def isbn_must_be_13_digits(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        digits = v.replace("-", "")
        if not digits.isdigit() or len(digits) != 13:
            raise ValueError("ISBN must be 13 digits long")
        return digits

# --- Response Model: What the client get back from the server ---
# Note: includes `id` (server-assigned), excludes nothing sensitive here
# but the pattern matters - you'd exclude `password` if it was a user model
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    year: int
    isbn: Optional[str] = None

# --- Request model for partial updates ---
class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Book Title")
    author: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Author full name")
    year: Optional[int] = Field(default=None, gt=0, le=2100, description="Year of publication")
    isbn: Optional[str] = Field(default=None, description="Book ISBN (Optional)")
