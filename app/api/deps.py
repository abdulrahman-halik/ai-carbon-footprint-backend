from fastapi import Depends, HTTPException, Request, status, Header, Query
import logging
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings
from app.schemas.user_schema import TokenData
from app.models.user_model import UserModel


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    authorization: str | None = Header(None),
    access_token: str | None = Query(None),
    query_token: str | None = Query(None, alias="token"),
):
    auth_token = token or access_token or query_token

    # Try Authorization header
    if not auth_token:
        authorization = authorization or request.headers.get("authorization")
        if authorization:
            scheme, _, credentials = authorization.partition(" ")
            if scheme.lower() == "bearer" and credentials:
                auth_token = credentials


    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Not authenticated."
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(auth_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logging.error("No sub in token payload")
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except JWTError as e:
        logging.error(f"JWT decode error: {e}")
        raise credentials_exception

    user = await UserModel.find_by_id(user_id)
    if user is None:
        logging.error(f"User not found for id: {user_id}")
        raise credentials_exception

    return user
