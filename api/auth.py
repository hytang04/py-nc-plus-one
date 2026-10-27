import os
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError

from api.models import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from db.connection import get_connection

load_dotenv()

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINS = 30

password_context = PasswordHasher()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


router = APIRouter(prefix="/api/auth", tags=["auth"])


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_context.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(UTC) + timedelta(minutes=JWT_EXPIRY_MINS),
    }
    token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    return token


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    credentials_exception = HTTPException(
        status_code=401,
        detail={"code": "UNAUTHORIZED", "message": "Could not validate credentials"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload["sub"]

        if user_id is None:
            raise credentials_exception
        return int(user_id)
    except (PyJWTError, KeyError, TypeError, ValueError):
        raise credentials_exception


@router.post("/login", status_code=200, response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    """
    Authenticate an existing user and return a JWT (JSON Web Token) for use on protected routes.

    Returns: `LoginResponse` object containing the token.

    Example request:
    ```
    {
        "email": "alice@example.com",
        "password": "securepassword123"
    }
    ```

    Example response:
    ```
    {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    ```
    """
    email, password = request.email, request.password
    if any(field is None or field.strip() == "" for field in (email, password)):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "BAD_REQUEST",
                "message": "Email and password fields are required",
            },
        )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email = %s", (request.email,))
    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "User not found"},
        )

    user_id = row[0]

    cur.execute("SELECT password FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "User not found"},
        )

    hashed_password = row[0]

    cur.close()
    conn.close()

    if verify_password(request.password, hashed_password):
        token = create_access_token(user_id)

        return LoginResponse(access_token=token, token_type="bearer")

    raise HTTPException(
        status_code=401, detail={"code": "UNAUTHORIZED", "message": "User not found"}
    )


@router.post("/register", status_code=201, response_model=dict[str, RegisterResponse])
def register(request: RegisterRequest) -> dict[str, RegisterResponse]:
    """
    Register a new user account.

    Returns: Dictionary with key `user` and value a `RegisterResponse` object.

    Example request:
    ```
    {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "password": "securepassword123"
    }
    ```

    Example response:
    ```
    {
        "user": {
            "id": 1,
            "name": "Alice Smith",
            "email": "alice@example.com",
            "created_at": "2025-06-01T10:00:00Z"
        }
    }
    ```
    """
    name, email, password = request.name, request.email, request.password
    if any(field is None or field.strip() == "" for field in (name, email, password)):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "BAD_REQUEST",
                "message": "Name, email, and password fields are required",
            },
        )

    conn = get_connection()
    cur = conn.cursor()
    hashed_password = hash_password(password)
    cur.execute(
        """
        INSERT INTO users (email, password, name)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING
        RETURNING id, name, email, created_at
        """,
        (email, hashed_password, name),
    )
    row = cur.fetchone()
    if row is None:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=409,
            detail={"code": "CONFLICT", "message": "Email already registered"},
        )

    conn.commit()
    cur.close()
    conn.close()

    return {
        "user": RegisterResponse(
            id=row[0],
            name=row[1],
            email=row[2],
            created_at=row[3].isoformat(),
        )
    }
