import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from jose import JWTError, jwt

# Check if the file exists
if os.path.exists("expenses/.env"):
    load_dotenv(dotenv_path="expenses/.env")


def create_access_token() -> str:
    """
    This function creates the access token.

    Parameters
    ----------
    expires_delta : Union[timedelta, None], optional
        The expiration time of the token, by default None
    """
    to_encode = {"user": os.getenv("USER_JWT")}
    encoded_jwt = jwt.encode(
        to_encode,
        key=os.getenv("SECRET_KEY"),
        algorithm=os.getenv("ALGORITHM"),
    )
    return encoded_jwt


async def check_access_token(
    credentials: HTTPBasicCredentials = Depends(HTTPBearer()),
) -> str:
    """
    This function checks the access token.

    Parameters
    ----------
    credentials : HTTPBasicCredentials, optional
        The credentials, by default Depends(HTTPBearer())
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You are not authorized to access this resource",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            key=os.getenv("SECRET_KEY"),
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_iss": False,
            },
        )
        if payload is None:
            raise credentials_exception
        return payload

    except JWTError:
        raise credentials_exception


if __name__ == "__main__":
    print(create_access_token())
