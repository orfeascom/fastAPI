from jose import JWTError, jwt, ExpiredSignatureError
from datetime import datetime, timedelta
from . import schemas
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .config import settings

oauth2Scheme = OAuth2PasswordBearer(tokenUrl='login')

# SECRET KEY
# ALGORITHM
# EXPIRATION TIME

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_expire_minutes

def create_access_token(data: dict):
    toEncode = data.copy()
    expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    toEncode.update({"exp" : expiration.replace(microsecond=0)})
    encodedJWT = jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)

    return encodedJWT

def verify_access_token(token: str, credentialsException):
    try:

        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id: str = payload.get("user_id")

        if id is None:
            raise credentialsException
        
        tokenData = schemas.TokenData(id=str(id))
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Signature has expired")
    except JWTError:
        raise credentialsException
    
    return tokenData
    
def get_current_user(token: str = Depends(oauth2Scheme)):
    credentialsException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", 
                                         headers={"WWW-Authenticate" : "Bearer"})
    
    token = verify_access_token(token, credentialsException)

    return token.id