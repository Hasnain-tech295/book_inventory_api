# models.py
# All your Pydantic models in one place — good habit from day one

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
import re

# --- Request model: what the client sends when creating a book ---
class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="Book title")
    author: str = Field(min_length=1, max_length=100, description="Author full name")
    year: int = Field(gt=0, le=2100, description="Publication year")
    isbn: Optional[str] = Field(default=None, description="ISBN-13 (optional)")

    # Custom validator: if ISBN is provided, it must be 13 digits
    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        digits = v.replace("-", "")
        if not digits.isdigit() or len(digits) != 13:
            raise ValueError("ISBN must be 13 digits")
        return digits  # store normalized (no hyphens)

# --- Response model: what the client gets back ---
# Note: includes `id` (server-assigned), excludes nothing sensitive here
# but the pattern matters — you'd exclude `password_hash` in a User model
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    year: int
    isbn: Optional[str] = None

# --- Request model for partial updates ---
class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, min_length=1, max_length=100)
    year: Optional[int] = Field(default=None, gt=0, le=2100)
    isbn: Optional[str] = None