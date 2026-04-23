from pydantic import BaseModel
from typing import Optional

# Common
class SuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None

class UploadResponse(BaseModel):
    url: str

# Auth
class TelegramAuthRequest(BaseModel):
    init_data: str

class AuthResponse(BaseModel):
    success: bool
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None

# Trading
class BalanceResponse(BaseModel):
    balance: float
    currency: str
    available: float
    pnl: float
    positions_count: int
    equity: float

class ConnectCapitalRequest(BaseModel):
    login: str
    password: str
    api_key: str
