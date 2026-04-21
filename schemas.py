from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
import re
from datetime import datetime

# Request model: What the client sends to the server
class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=200)
    year: int = Field(gt=0, le=2026)
    price: float = Field(gt=0)
    genre: Optional[str] = Field(default=None, max_length=50)
    isbn: Optional[str] = Field(default=None, description="ISBN-13")
    
    # Custom valiator: if ISBN is provided, it must be of 13 digits
    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        digits = value.replace("-", "")
        if not digits.isdigit() or len(digits) != 13:
            raise ValueError("ISBN must be 13 digits")
        return digits

    @field_validator('year')
    @classmethod
    def year_not_in_future(cls, v):
        if v is not None and v > datetime.now().year:
            raise ValueError(f"Year cannot be in the future")
        return v

# Response model: What the server sends back to the client
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    year: int
    price: float
    isbn: Optional[str] = None
    genre: Optional[str] = None


# Request model for partial update
class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, min_length=1, max_length=200)
    year: Optional[int] = Field(default=None, gt=0, le=datetime.now().year)
    price: Optional[float] = Field(default=None, gt=0)
    isbn: Optional[str] = Field(default=None)

    @field_validator('year')
    @classmethod
    def year_not_in_future(cls, v):
        if v is not None and v > datetime.now().year:
            raise ValueError(f"Year cannot be in the future")
        return v