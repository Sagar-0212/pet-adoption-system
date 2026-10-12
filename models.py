"""
Data models for Pet Adoption & Management System.
Defines SQLAlchemy ORM models (PetModel, AdoptionRequestModel, UserModel, FavoriteModel)
and Pydantic schemas (Pet, AdoptionRequest, StatusUpdate, User, UserCreate, UserLogin, UserResponse, Token).
Author: Sagar / Neal (S2_Neal)
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


# ============================================================================
# SQLAlchemy ORM Models (Persistent Database)
# ============================================================================

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    favorites = relationship(
        "FavoriteModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class FavoriteModel(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pet_id = Column(String(50), ForeignKey("pets.pet_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "pet_id", name="uq_user_pet_favorite"),
    )

    user = relationship("UserModel", back_populates="favorites")
    pet = relationship("PetModel", back_populates="favorites")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "pet_id": self.pet_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "pet": self.pet.to_dict() if self.pet else None,
        }


class PetModel(Base):
    __tablename__ = "pets"

    pet_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="available")
    gender = Column(String(20), nullable=True, default="Unknown")
    size = Column(String(20), nullable=True, default="Medium")
    age_category = Column(String(20), nullable=True, default="Adult")

    adoptions = relationship(
        "AdoptionRequestModel",
        back_populates="pet",
        cascade="all, delete-orphan"
    )
    favorites = relationship(
        "FavoriteModel",
        back_populates="pet",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "pet_id": self.pet_id,
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "age": self.age,
            "description": self.description,
            "status": self.status,
            "gender": self.gender or "Unknown",
            "size": self.size or "Medium",
            "age_category": self.age_category or "Adult",
        }


class AdoptionRequestModel(Base):
    __tablename__ = "adoption_requests"

    request_id = Column(String(50), primary_key=True, index=True)
    pet_id = Column(String(50), ForeignKey("pets.pet_id", ondelete="CASCADE"), nullable=False, index=True)
    adopter_name = Column(String(100), nullable=False)
    adopter_email = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    pet = relationship("PetModel", back_populates="adoptions")

    def to_dict(self):
        return {
            "request_id": self.request_id,
            "pet_id": self.pet_id,
            "adopter_name": self.adopter_name,
            "adopter_email": self.adopter_email,
            "message": self.message,
            "status": self.status,
            "user_id": self.user_id,
        }


# ============================================================================
# Pydantic Schemas (Request/Response Validation)
# ============================================================================

class Pet(BaseModel):
    pet_id: str
    name: str
    species: str
    breed: str
    age: int
    description: str
    status: str = "available"
    gender: Optional[str] = "Unknown"
    size: Optional[str] = "Medium"
    age_category: Optional[str] = "Adult"


class AdoptionRequest(BaseModel):
    request_id: str
    pet_id: str
    adopter_name: str
    adopter_email: str
    message: str
    status: str = "pending"
    user_id: Optional[int] = None


class StatusUpdate(BaseModel):
    status: str


class User(BaseModel):
    email: str
    full_name: str
    username: Optional[str] = None
    is_admin: bool = False


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    username: Optional[str] = None


UserRegister = UserCreate


class UserLogin(BaseModel):
    email: Optional[str] = None
    password: str
    username: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_admin: bool = False
    created_at: Optional[datetime] = None
    username: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


TokenResponse = Token
