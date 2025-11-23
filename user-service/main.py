from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI(title="User Service", version="1.0.0")

USERS_FILE = "users.json"

# Модели данных
class User(BaseModel):
    id: int
    name: str
    email: str

class UserCreate(BaseModel):
    name: str
    email: str

# Вспомогательные функции для работы с JSON
def read_users_file() -> List[dict]:
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_users_file(users: List[dict]):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

# API endpoints
@app.get("/users", response_model=List[User])
async def get_users():
    """Получить всех пользователей"""
    users = read_users_file()
    return users

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Получить пользователя по ID"""
    users = read_users_file()
    user = next((u for u in users if u["id"] == user_id), None)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Создать нового пользователя"""
    users = read_users_file()
    
    # Генерируем новый ID
    new_id = max([u["id"] for u in users], default=0) + 1
    
    new_user = {
        "id": new_id,
        "name": user_data.name,
        "email": user_data.email
    }
    
    users.append(new_user)
    write_users_file(users)
    
    return new_user

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "OK", "service": "user-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)