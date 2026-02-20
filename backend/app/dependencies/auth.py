"""Authentication dependencies for JWT verification.

This module provides dependencies for extracting and validating
user identity from JWT tokens. The implementation is designed
to work with any JWT provider (Better Auth, Auth0, custom).
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWTError

from app.config import settings
from app.core.exceptions import UnauthorizedException

# Configure logger
logger = logging.getLogger(__name__)

# Log JWT library info at import time
try:
    import jwt
    import os
    lib_path = getattr(jwt, "__file__", "unknown")
    lib_ver = getattr(jwt, "__version__", "unknown")
    is_pyjwt = hasattr(jwt, "PyJWTError")
    logger.info(f"JWT Library loaded: {lib_path}, Version: {lib_ver}, IsPyJWT: {is_pyjwt}")
except Exception as e:
    logger.error(f"Error identifying JWT library: {e}")

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


class TokenData:
    """Parsed token payload data.

    Attributes:
        user_id: The user identifier extracted from the token.
        email: Optional email from the token.
        exp: Optional expiration timestamp.
    """

    def __init__(
        self,
        user_id: UUID,
        email: Optional[str] = None,
        exp: Optional[int] = None,
    ):
        self.user_id = user_id
        self.email = email
        self.exp = exp


def decode_token(token: str, request: Optional[Request] = None) -> TokenData:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string.
        request: Optional FastAPI request for logging client info.

    Returns:
        TokenData containing extracted user information.

    Raises:
        UnauthorizedException: If token is invalid or expired.
    """
    try:
        algo = settings.ALGORITHM.strip()
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[algo],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException(detail="Token missing user identifier")

        token_data = TokenData(
            user_id=UUID(user_id),
            email=payload.get("email"),
            exp=payload.get("exp"),
        )

        # Log successful token verification
        client_ip = _get_client_ip(request)
        logger.info(
            f"Token verified successfully for user {token_data.user_id} "
            f"(email: {token_data.email}) from IP: {client_ip}"
        )

        return token_data
    except PyJWTError as e:
        # Log failed token verification
        client_ip = _get_client_ip(request)
        error_type = _get_jwt_error_type(str(e))
        logger.warning(
            f"Token verification failed: {error_type} from IP: {client_ip}"
        )
        raise UnauthorizedException(detail=f"Invalid token: {error_type}")


def _get_client_ip(request: Optional[Request]) -> str:
    """Extract client IP address from request."""
    if request is None:
        return "unknown"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _get_jwt_error_type(error_msg: str) -> str:
    """Categorize JWT error for logging."""
    error_lower = error_msg.lower()
    if "expired" in error_lower:
        return "expired_token"
    elif "signature" in error_lower:
        return "invalid_signature"
    elif "audience" in error_lower:
        return "invalid_audience"
    elif "issuer" in error_lower:
        return "invalid_issuer"
    else:
        return "invalid_token"


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    request: Request = None,
) -> UUID:
    """
    Dependency to get the current authenticated user from JWT token.

    This dependency validates the Bearer token or Cookie and returns the user_id.

    Args:
        credentials: HTTP Authorization credentials from Bearer token.
        request: FastAPI request for logging client info.

    Returns:
        UUID: The authenticated user's ID.

    Raises:
        HTTPException: 401 if no valid token is provided.
    """
    token = None
    
    # 1. Try Bearer Token
    if credentials:
        token = credentials.credentials
    
    # 2. Try Cookie if no Bearer Token
    if not token and request:
        token = request.cookies.get("jwt_token") or request.cookies.get("token")
        
    # 3. Try query param (useful for SSE)
    if not token and request:
        token = request.query_params.get("token")
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = decode_token(token, request)
    return token_data.user_id


def create_access_token(
    user_id: UUID,
    email: Optional[str] = None,
    expires_delta: Optional[int] = None,
) -> str:
    """
    Create a JWT access token for a user.

    This utility is provided for testing and future use when
    implementing user registration/login flows.

    Args:
        user_id: The user's UUID.
        email: Optional email to include in token.
        expires_delta: Optional expiration time in minutes.

    Returns:
        str: Encoded JWT token.
    """
    from datetime import datetime, timedelta, timezone

    if expires_delta is None:
        expires_delta = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)

    to_encode = {
        "sub": str(user_id),
        "exp": int(expire.timestamp()),
    }

    if email:
        to_encode["email"] = email

    algo = settings.ALGORITHM.strip()
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=algo,
    )

    return encoded_jwt
