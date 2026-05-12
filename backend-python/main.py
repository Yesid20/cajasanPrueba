from datetime import datetime, timedelta
from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
from passlib.context import CryptContext
import secrets

#
ACCESS_EXPIRE_MINUTES = 3
REFRESH_EXPIRE_DAYS = 1

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()

app = FastAPI(title="Products API - Auth opaco (no SECRET_KEY)")

# 
class Item(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int

    @field_validator("price")
    @classmethod
    def price_non_negative(cls, v):
        if v < 0:
            raise ValueError("price must be >= 0")
        return v

    @field_validator("stock")
    @classmethod
    def stock_non_negative(cls, v):
        if v < 0:
            raise ValueError("stock must be >= 0")
        return v

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    admin: bool
    role: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

#
def hash_password(pw: str) -> str:
    return pwd_ctx.hash(pw)

users_db: Dict[str, UserInDB] = {
    "alice": UserInDB(username="alice", hashed_password=hash_password("alicepass"), admin=True, role="admin"),
    "bob":   UserInDB(username="bob",   hashed_password=hash_password("bobpass"),   admin=False, role="user"),
}

#
access_store: Dict[str, Dict] = {}
refresh_store: Dict[str, Dict] = {}

#
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token_opaque(username: str, role: str) -> (str, datetime):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    access_store[token] = {"username": username, "role": role, "expires_at": expires_at}
    return token, expires_at

def create_refresh_token_opaque(username: str) -> (str, datetime):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    refresh_store[token] = {"username": username, "expires_at": expires_at}
    return token, expires_at

def validate_access_token_opaque(token: str) -> Optional[Dict]:
    data = access_store.get(token)
    if not data:
        return None
    if data["expires_at"] < datetime.utcnow():
        access_store.pop(token, None)
        return None
    return data

def validate_refresh_token_opaque(token: str) -> Optional[str]:
    data = refresh_store.get(token)
    if not data:
        return None
    if data["expires_at"] < datetime.utcnow():
        refresh_store.pop(token, None)
        return None
    return data["username"]

def revoke_refresh_token(token: str):
    refresh_store.pop(token, None)

def revoke_access_token(token: str):
    access_store.pop(token, None)
    
# ---------------- Dependencias ----------------
def get_current_user_opaque(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> UserInDB:
    token = creds.credentials
    data = validate_access_token_opaque(token)
    if not data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    username = data["username"]
    user = users_db.get(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user

def require_admin(user: UserInDB = Depends(get_current_user_opaque)):
    if not user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere privilegios de administrador")
    return user

#
@app.post("/auth/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    access_token, access_exp = create_access_token_opaque(user.username, user.role)
    refresh_token, refresh_exp = create_refresh_token_opaque(user.username)
    expires_in = int((access_exp - datetime.utcnow()).total_seconds())

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in
    )

@app.post("/auth/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(req: RefreshRequest):
    """
    Refresh: valida refresh token opaco, rota refresh token (revoca el viejo y emite uno nuevo),
    emite nuevo access token opaco.
    """
    username = validate_refresh_token_opaque(req.refresh_token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido o expirado")

    revoke_refresh_token(req.refresh_token)

    user = users_db.get(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    access_token, access_exp = create_access_token_opaque(user.username, user.role)
    new_refresh_token, refresh_exp = create_refresh_token_opaque(user.username)
    expires_in = int((access_exp - datetime.utcnow()).total_seconds())

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=expires_in
    )

@app.post("/auth/logout", status_code=status.HTTP_200_OK)
async def logout(req: LogoutRequest):
    """
    Logout: revoca refresh token. Opcionalmente se pueden revocar todos los access tokens del usuario.
    """
    username = validate_refresh_token_opaque(req.refresh_token)
    if username:
        revoke_refresh_token(req.refresh_token)
        revoke_all_access_tokens_for_user(username)
    return {"message": "Sesión cerrada (refresh token revocado)"}

items: List[Item] = [
    Item(id=1, name="Laptop", category="Electrónica", price=1200.0, stock=5),
    Item(id=2, name="Mouse",  category="Accesorios",  price=25.0,   stock=50),
]

#
@app.get("/products", status_code=status.HTTP_200_OK)
async def get_products(current_user: UserInDB = Depends(get_current_user_opaque)):
    return items

@app.get("/products/{id}", status_code=status.HTTP_200_OK)
async def get_product(id: int, current_user: UserInDB = Depends(get_current_user_opaque)):
    for item in items:
        if item.id == id:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(item: Item, current_user: UserInDB = Depends(require_admin)):
    if any(i.id == item.id for i in items):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID ya existe")
    items.append(item)
    return {"message": "Producto creado", "product": item}

@app.patch("/products/{id}/stock", status_code=status.HTTP_200_OK)
async def update_stock(id: int, stock: int, current_user: UserInDB = Depends(get_current_user_opaque)):
    for item in items:
        if item.id == id:
            if stock < 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="stock debe ser >= 0")
            item.stock = stock
            return {"message": "Stock actualizado", "product": item}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
