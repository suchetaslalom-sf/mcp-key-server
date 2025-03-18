from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# API Key Schemas
class ApiKeyBase(BaseModel):
    name: str
    service: str
    description: Optional[str] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None


class ApiKeyCreate(ApiKeyBase):
    key: str


class ApiKeyUpdate(BaseModel):
    name: Optional[str] = None
    service: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ApiKey(ApiKeyBase):
    id: int
    key: str
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# NPM Package Schemas
class NpmPackageBase(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    is_private: bool = False
    package_json: Optional[Dict[str, Any]] = None


class NpmPackageCreate(NpmPackageBase):
    pass


class NpmPackageUpdate(BaseModel):
    version: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None
    package_json: Optional[Dict[str, Any]] = None


class NpmPackage(NpmPackageBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    is_admin: Optional[bool] = False
