from fastapi import Depends, HTTPException, Request, status, Header, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import logging

from app.core.config import settings
from app.schemas.user_schema import TokenData
from app.models.user_model import UserModel

# Fallback auto_error=False ensures custom parsing fallback mechanisms do not auto-fail
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False,
)


async def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    authorization: str | None = Header(None),
    access_token: str | None = Query(None),
    query_token: str | None = Query(None, alias="token"),
):
    # 1. Fallback extraction cascade
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
            detail="Not authenticated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 2. Decode Token
    try:
        payload = jwt.decode(
            auth_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id: str = payload.get("sub")

        if user_id is None:
            logging.error("JWT Payload validation missing sub claim field.")
            raise credentials_exception

        token_data = TokenData(id=user_id)

    except JWTError as e:
        logging.error(f"JWT signature validation failure: {e}")
        raise credentials_exception

    # 3. DB Entity verification
    user = await UserModel.find_by_id(user_id)

    if user is None:
        logging.error(
            f"Authenticated token entity matching id '{user_id}' missing in Database."
        )
        raise credentials_exception

    return user