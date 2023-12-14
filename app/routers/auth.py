from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=['Authentication'])

# User login
@router.post('/login', response_model=schemas.Token)
def log(userCredentials: OAuth2PasswordRequestForm = Depends(), 
        db: Session = Depends(database.get_db)):

    user =db.query(models.User).filter(
        models.User.email == userCredentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials")
    
    if not utils.verify(userCredentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials")
    
    accessToken = oauth2.create_access_token(data = {"user_id" : user.id})
    
    return {"access_token" : accessToken, "token_type" : "bearer"}