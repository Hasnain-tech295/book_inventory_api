# A minimal but complete REST API

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# --- In-memory "database" (a dict) ---
users_db: dict[int, dict] = {
    1: {"id": 1, "name": "Ada Lovelace", "email": "ada@example.com"},
    2: {"id": 2, "name": "Alan Turing",  "email": "alan@example.com"},
}

# --- Request model for creating a user ---
class UserCreate(BaseModel):
    name: str
    email: str

# --- GET all users ---
@app.get("/users")
def list_users():
    return list(users_db.values())

# --- GET one user ---
@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

# --- POST create user ---
@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    new_id = max(users_db.keys()) + 1
    new_user = {"id": new_id, "name": user.name, "email": user.email}
    users_db[new_id] = new_user
    return new_user

# --- DELETE user ---
@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]