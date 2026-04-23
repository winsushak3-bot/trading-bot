from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.schemas import BalanceResponse, ConnectCapitalRequest, SuccessResponse
from backend.core.deps import get_session, get_current_user_id
from shared.database.repo.accounts import AccountRepo
from shared.services.capital import capital_client

router = APIRouter()

@router.post("/connect-capital", response_model=SuccessResponse)
async def connect_capital(
    request: ConnectCapitalRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Подключает Capital.com Demo аккаунт.
    """
    # Проверяем подключение
    data, error = await capital_client.check_connection(
        login=request.login,
        password=request.password,
        api_key=request.api_key
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # Сохраняем в БД (зашифрованно)
    account_repo = AccountRepo(session)
    await account_repo.add_account(
        user_id=user_id,
        api_key=request.api_key,
        password=request.password,
        account_name=request.login,
        broker="capital"
    )
    
    return SuccessResponse(success=True, message="Capital.com подключен")

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Получает баланс с Capital.com.
    """
    account_repo = AccountRepo(session)
    account = await account_repo.get_account(user_id, broker="capital")
    
    if not account:
        raise HTTPException(status_code=404, detail="Capital.com не подключен")
    
    data, error = await capital_client.check_connection(
        login=account['account_name'],
        password=account['password'],
        api_key=account['api_key']
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return BalanceResponse(
        balance=data['balance'],
        currency=data['currency'],
        available=data['available'],
        pnl=data['pnl'],
        positions_count=data['positions_count'],
        equity=data['equity'],
    )
