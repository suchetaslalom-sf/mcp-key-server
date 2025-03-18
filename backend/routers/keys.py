from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from security import get_current_active_user, get_current_admin_user

router = APIRouter()


@router.post("/", response_model=schemas.ApiKey, status_code=status.HTTP_201_CREATED)
def create_api_key(api_key: schemas.ApiKeyCreate,
                   current_user = Depends(get_current_active_user),
                   db: Session = Depends(get_db)):
    # Create new API key
    db_api_key = models.ApiKey(
        name=api_key.name,
        key=api_key.key,
        service=api_key.service,
        description=api_key.description,
        is_active=api_key.is_active,
        metadata=api_key.metadata,
        owner_id=current_user.id
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key


@router.get("/", response_model=List[schemas.ApiKey])
def get_api_keys(service: Optional[str] = None,
                 is_active: Optional[bool] = None,
                 current_user = Depends(get_current_active_user),
                 db: Session = Depends(get_db)):
    # Query API keys owned by current user
    query = db.query(models.ApiKey).filter(models.ApiKey.owner_id == current_user.id)
    
    # Apply filters if provided
    if service:
        query = query.filter(models.ApiKey.service == service)
    if is_active is not None:
        query = query.filter(models.ApiKey.is_active == is_active)
    
    return query.all()


@router.get("/admin", response_model=List[schemas.ApiKey])
def get_all_api_keys(service: Optional[str] = None,
                     is_active: Optional[bool] = None,
                     skip: int = 0,
                     limit: int = 100,
                     current_user = Depends(get_current_admin_user),
                     db: Session = Depends(get_db)):
    # Admin endpoint to query all API keys
    query = db.query(models.ApiKey)
    
    # Apply filters if provided
    if service:
        query = query.filter(models.ApiKey.service == service)
    if is_active is not None:
        query = query.filter(models.ApiKey.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{key_id}", response_model=schemas.ApiKey)
def get_api_key(key_id: int,
                current_user = Depends(get_current_active_user),
                db: Session = Depends(get_db)):
    # Query specific API key
    db_api_key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    
    # Check if API key exists and belongs to the current user
    if db_api_key is None:
        raise HTTPException(status_code=404, detail="API key not found")
    if db_api_key.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this API key")
    
    return db_api_key


@router.put("/{key_id}", response_model=schemas.ApiKey)
def update_api_key(key_id: int,
                   api_key_update: schemas.ApiKeyUpdate,
                   current_user = Depends(get_current_active_user),
                   db: Session = Depends(get_db)):
    # Query specific API key
    db_api_key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    
    # Check if API key exists and belongs to the current user
    if db_api_key is None:
        raise HTTPException(status_code=404, detail="API key not found")
    if db_api_key.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this API key")
    
    # Update API key fields if provided
    if api_key_update.name is not None:
        db_api_key.name = api_key_update.name
    if api_key_update.service is not None:
        db_api_key.service = api_key_update.service
    if api_key_update.description is not None:
        db_api_key.description = api_key_update.description
    if api_key_update.is_active is not None:
        db_api_key.is_active = api_key_update.is_active
    if api_key_update.metadata is not None:
        db_api_key.metadata = api_key_update.metadata
    
    db.commit()
    db.refresh(db_api_key)
    return db_api_key


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(key_id: int,
                   current_user = Depends(get_current_active_user),
                   db: Session = Depends(get_db)):
    # Query specific API key
    db_api_key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    
    # Check if API key exists and belongs to the current user
    if db_api_key is None:
        raise HTTPException(status_code=404, detail="API key not found")
    if db_api_key.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this API key")
    
    # Delete the API key
    db.delete(db_api_key)
    db.commit()
    return None
