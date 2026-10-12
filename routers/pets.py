"""
Pet Management Router.
Handles pet registration, retrieval, updating, deletion, and listing backed by persistent database.
Author: Sagar / Neal (S2_Neal)
"""
import collections.abc
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db, SessionLocal, init_db
from models import Pet, PetModel

router = APIRouter(prefix="/pets", tags=["Pet Management"])


# Database-backed dictionary proxy for backward compatibility with existing tests
class PetDictProxy(collections.abc.MutableMapping):
    def __getitem__(self, key):
        init_db()
        with SessionLocal() as db:
            p = db.query(PetModel).filter(PetModel.pet_id == key).first()
            if not p:
                raise KeyError(key)
            return p.to_dict()

    def __setitem__(self, key, val):
        init_db()
        with SessionLocal() as db:
            p = db.query(PetModel).filter(PetModel.pet_id == key).first()
            if not p:
                data = {k: v for k, v in val.items() if k != "pet_id"}
                p = PetModel(pet_id=key, **data)
                db.add(p)
            else:
                for k, v in val.items():
                    if hasattr(p, k):
                        setattr(p, k, v)
            db.commit()

    def __delitem__(self, key):
        init_db()
        with SessionLocal() as db:
            p = db.query(PetModel).filter(PetModel.pet_id == key).first()
            if not p:
                raise KeyError(key)
            db.delete(p)
            db.commit()

    def __iter__(self):
        init_db()
        with SessionLocal() as db:
            return iter([p.pet_id for p in db.query(PetModel.pet_id).all()])

    def __len__(self):
        init_db()
        with SessionLocal() as db:
            return db.query(PetModel).count()

    def __contains__(self, key):
        init_db()
        with SessionLocal() as db:
            return db.query(PetModel).filter(PetModel.pet_id == key).first() is not None

    def clear(self):
        init_db()
        with SessionLocal() as db:
            db.query(PetModel).delete()
            db.commit()

    def values(self):
        init_db()
        with SessionLocal() as db:
            return [p.to_dict() for p in db.query(PetModel).all()]

    def pop(self, key, default=None):
        init_db()
        with SessionLocal() as db:
            p = db.query(PetModel).filter(PetModel.pet_id == key).first()
            if not p:
                if default is not None:
                    return default
                raise KeyError(key)
            d = p.to_dict()
            db.delete(p)
            db.commit()
            return d


pets_db = PetDictProxy()


@router.post("", response_model=dict)
@router.post("/", response_model=dict)
def register_pet(pet: Pet, db: Session = Depends(get_db)):
    """
    Register a new pet in the persistent database.
    Returns 400 if pet_id already exists.
    """
    existing = db.query(PetModel).filter(PetModel.pet_id == pet.pet_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Pet already exists")

    new_pet = PetModel(
        pet_id=pet.pet_id,
        name=pet.name,
        species=pet.species,
        breed=pet.breed,
        age=pet.age,
        description=pet.description,
        status=pet.status or "available",
        gender=getattr(pet, "gender", "Unknown") or "Unknown",
        size=getattr(pet, "size", "Medium") or "Medium",
        age_category=getattr(pet, "age_category", "Adult") or "Adult",
    )
    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)
    return {"message": "Pet registered", "data": new_pet.to_dict()}


@router.get("", response_model=List[dict])
@router.get("/", response_model=List[dict])
def get_pets(db: Session = Depends(get_db)):
    """
    Retrieve all registered pets from persistent database.
    """
    pets = db.query(PetModel).all()
    return [p.to_dict() for p in pets]


@router.get("/{pet_id}", response_model=dict)
def get_pet(pet_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific pet by ID.
    Returns 404 if not found.
    """
    pet = db.query(PetModel).filter(PetModel.pet_id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet.to_dict()


@router.put("/{pet_id}", response_model=dict)
def update_pet(pet_id: str, pet: Pet, db: Session = Depends(get_db)):
    """
    Update an existing pet by ID in persistent database.
    Returns 404 if not found.
    """
    db_pet = db.query(PetModel).filter(PetModel.pet_id == pet_id).first()
    if not db_pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    db_pet.name = pet.name
    db_pet.species = pet.species
    db_pet.breed = pet.breed
    db_pet.age = pet.age
    db_pet.description = pet.description
    if pet.status:
        db_pet.status = pet.status
    if hasattr(db_pet, "gender") and getattr(pet, "gender", None):
        db_pet.gender = pet.gender
    if hasattr(db_pet, "size") and getattr(pet, "size", None):
        db_pet.size = pet.size
    if hasattr(db_pet, "age_category") and getattr(pet, "age_category", None):
        db_pet.age_category = pet.age_category

    db.commit()
    db.refresh(db_pet)
    return {"message": "Pet updated", "data": db_pet.to_dict()}


@router.delete("/{pet_id}", response_model=dict)
def delete_pet(pet_id: str, db: Session = Depends(get_db)):
    """
    Delete a pet by ID from persistent database.
    Returns 404 if not found.
    """
    db_pet = db.query(PetModel).filter(PetModel.pet_id == pet_id).first()
    if not db_pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    db.delete(db_pet)
    db.commit()
    return {"message": "Pet deleted", "pet_id": pet_id}
