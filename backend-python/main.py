from datetime import datetime, timedelta
from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from jose import JWTError, jwt
import os
 
SECRET_KEY = "prueba-superada-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3
REFRESH_TOKEN_EXPIRE_DAYS = 1
 
bearer = HTTPBearer()
 
app = FastAPI(title="Products API - Auth JWT")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
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
 
class User(BaseModel):
    username: str
    admin: bool
    role: str
 
class UserInDB(User):
    password: str
 
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
 
class RefreshRequest(BaseModel):
    refresh_token: str
 
class LogoutRequest(BaseModel):
    refresh_token: str
 
users_db: Dict[str, UserInDB] = {
    "alice": UserInDB(username="alice", password="alicepass", admin=True, role="admin"),
    "bob":   UserInDB(username="bob",   password="bobpass",   admin=False, role="user"),
}
 
revoked_tokens: set = set()
 
items: List[Item] = [
    Item(id=1, name="Camiseta", category="Ropa", price=1200.0, stock=25),
    Item(id=2, name="Pantalon",  category="Ropa",  price=25.0,   stock=50),
]
 
def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = users_db.get(username)
    if not user:
        return None
    if user.password != password:
        return None
    return user
 
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
 
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
 
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
 
def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> User:
    token = creds.credentials
    payload = verify_token(token)
    
    username = payload.get("sub")
    user = users_db.get(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    
    return User(username=user.username, admin=user.admin, role=user.role)
 
def require_admin(user: User = Depends(get_current_user)) -> User:
    """Requiere que el usuario sea admin"""
    if not user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere privilegios de administrador")
    return user
 
@app.post("/auth/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
 
    # Crear tokens JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.username},
        expires_delta=refresh_token_expires
    )
 
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  
    )
 
@app.post("/auth/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(req: RefreshRequest):
    """
    Refresh: valida refresh_token JWT, emite nuevo access_token y nuevo refresh_token
    """
    try:
        payload = jwt.decode(req.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if not username or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")
        
        if req.refresh_token in revoked_tokens:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token fue revocado")
        
        user = users_db.get(username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=access_token_expires
        )
        
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = create_refresh_token(
            data={"sub": user.username},
            expires_delta=refresh_token_expires
        )
        
        revoked_tokens.add(req.refresh_token)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido o expirado")
 
@app.post("/auth/logout", status_code=status.HTTP_200_OK)
async def logout(req: LogoutRequest):
    """Logout: revoca el refresh_token"""
    try:
        payload = jwt.decode(req.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        revoked_tokens.add(req.refresh_token)
        return {"message": "Sesión cerrada (refresh token revocado)"}
    except JWTError:
        return {"message": "Sesión cerrada"}
 
@app.get("/products", status_code=status.HTTP_200_OK)
async def get_products(current_user: User = Depends(get_current_user)):
    """Obtiene todos los productos (requiere autenticación)"""
    return items
 
@app.get("/products/{id}", status_code=status.HTTP_200_OK)
async def get_product(id: int, current_user: User = Depends(get_current_user)):
    """Obtiene un producto por ID"""
    for item in items:
        if item.id == id:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
 
@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(item: Item, current_user: User = Depends(require_admin)):
    """Crea un producto (requiere ser admin)"""
    if any(i.id == item.id for i in items):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID ya existe")
    items.append(item)
    return {"message": "Producto creado", "product": item}
 
@app.patch("/products/{id}/stock", status_code=status.HTTP_200_OK)
async def update_stock(id: int, stock: int, current_user: User = Depends(get_current_user)):
    """Actualiza el stock de un producto"""
    for item in items:
        if item.id == id:
            if stock < 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="stock debe ser >= 0")
            item.stock = stock
            return {"message": "Stock actualizado", "product": item}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")