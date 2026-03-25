from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.schemas.auth import Token, TokenData, User, UserInDB
from app.utils.auth import (
    SECRET_KEY, 
    ALGORITHM, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password,
    create_access_token,
    get_password_hash
)

router = APIRouter()

# This tells FastAPI where the client should send the login request to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# --- MOCK DATABASE ---
# Replace this with your actual database call (e.g., using Drizzle/SQLModel)
# The ID is generated as a UUID string to match your Flutter session expectations
MOCK_USERS_DB = {
    "admin@nova.com": {
        "id": "1",
        "username": "admin@nova.com",
        "email": "admin@nova.com",
        "hashed_password": get_password_hash("password123"),
    }
}

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

# --- DEPENDENCY ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to inject the current authenticated user into any endpoint.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    user = get_user(MOCK_USERS_DB, username=token_data.username)
    if user is None:
        raise credentials_exception
        
    return User(id=user.id, username=user.username, email=user.email)

# --- ENDPOINTS ---
@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates a user and returns a JWT token.
    FastAPI's OAuth2PasswordRequestForm automatically parses form-urlencoded data.
    """
    user = get_user(MOCK_USERS_DB, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}