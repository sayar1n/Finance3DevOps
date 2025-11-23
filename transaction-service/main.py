from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import httpx
import os

app = FastAPI(title="Transaction Service", version="1.0.0")

TRANSACTIONS_FILE = "transactions.json"
USER_SERVICE_URL = "http://user-service:8000"

# Модели данных
class Transaction(BaseModel):
    id: int
    amount: float
    category: str
    description: Optional[str] = ""
    type: str  # "income" или "expense"
    date: str
    userId: int

class TransactionCreate(BaseModel):
    amount: float
    category: str
    description: Optional[str] = ""
    type: str
    date: Optional[str] = None
    userId: int

class TransactionWithUser(Transaction):
    user: Optional[dict] = None

# Вспомогательные функции
def read_transactions_file() -> List[dict]:
    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_transactions_file(transactions: List[dict]):
    with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)

# API endpoints
@app.get("/transactions", response_model=List[Transaction])
async def get_transactions():
    """Получить все транзакции"""
    transactions = read_transactions_file()
    return transactions

@app.get("/transactions/{transaction_id}", response_model=TransactionWithUser)
async def get_transaction(transaction_id: int):
    """Получить транзакцию по ID с информацией о пользователе"""
    transactions = read_transactions_file()
    transaction = next((t for t in transactions if t["id"] == transaction_id), None)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Межсервисное взаимодействие: получаем данные пользователя
    try:
        async with httpx.AsyncClient() as client:
            user_response = await client.get(f"{USER_SERVICE_URL}/users/{transaction['userId']}")
            if user_response.status_code == 200:
                transaction["user"] = user_response.json()
    except httpx.RequestError:
        # Если сервис пользователей недоступен, продолжаем без user данных
        pass
    
    return transaction

@app.post("/transactions", response_model=Transaction)
async def create_transaction(transaction_data: TransactionCreate):
    """Создать новую транзакцию"""
    transactions = read_transactions_file()
    
    # Генерируем новый ID
    new_id = max([t["id"] for t in transactions], default=0) + 1
    
    new_transaction = {
        "id": new_id,
        "amount": transaction_data.amount,
        "category": transaction_data.category,
        "description": transaction_data.description,
        "type": transaction_data.type,
        "date": transaction_data.date or "2024-01-15",  # Простая дата для примера
        "userId": transaction_data.userId
    }
    
    transactions.append(new_transaction)
    write_transactions_file(transactions)
    
    return new_transaction

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "OK", "service": "transaction-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)