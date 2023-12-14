from fastapi import status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Optional
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)

@router.post("", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), 
         userID: int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {vote.post_id} does not exist")

    voteQuery = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,
                                             models.Vote.user_id == userID)
    queryResult = voteQuery.first()
    if (str(vote.direction) == "1"):
        if queryResult:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"user {userID} has already voted that post")
        votePost = models.Vote(post_id = vote.post_id, user_id = userID)
        db.add(votePost)
        db.commit()

        return {"message" : "successfully upvoted"}
    
    else:
        if not queryResult:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Vote does not exist")
        voteQuery.delete(synchronize_session=False)
        db.commit()

        return {"message" : "successfully removed vote"}