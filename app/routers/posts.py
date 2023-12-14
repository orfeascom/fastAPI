from fastapi import status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
    )

# Get all posts , response_model=schemas.PostOut
@router.get("", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), 
              userID: int = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0, title: Optional[str] = ""):
    
    # skip is used for front end pagination (results per page)
    # posts = db.query(models.Post).filter(
    #                                     models.Post.title.contains(title)
    #                                     ).limit(limit).offset(skip).all()
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("Votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
            models.Post.id).filter(
                models.Post.title.contains(title)).limit(limit).offset(skip).all()
    
    # .order_by(func.count(models.Vote.post_id).desc()) before .filter()
    return posts


# Create post
@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), 
                userID: int = Depends(oauth2.get_current_user)):
    
    new_post = models.Post(owner_id = userID, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# Get a single post by ID
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), 
             userID: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post, func.count(models.Vote.post_id).label("Votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
            models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found!")
    return post


# Delete a single post
@router.delete("/{id}")
def delete_post(id: int, db: Session = Depends(get_db), 
                userID: int = Depends(oauth2.get_current_user)):

    postQuery = db.query(models.Post).filter(models.Post.id == id)

    if not postQuery.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    postQuery.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Update a single post
@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostBase, db: Session = Depends(get_db),
                userID: int = Depends(oauth2.get_current_user)):

    postQuery = db.query(models.Post).filter(models.Post.id == id)

    updatedPost = postQuery.first()

    if not updatedPost:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    postQuery.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return postQuery.first()