"""
Admin Management Router.
Handles pet deletion, pet status updates, adoption approvals with cascade,
and dashboard metrics via persistent database.
Author: Harshwardhan (S4_Harshwardhan)
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import StatusUpdate, PetModel, AdoptionRequestModel
from routers.pets import pets_db
from routers.adoptions import adoptions_db

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.put("/adoptions/{request_id}/status")
def update_adoption_status(request_id: str, update: StatusUpdate, db: Session = Depends(get_db)):
    """
    Update adoption request status (e.g., 'approved', 'rejected').
    If approved, cascades pet status to 'adopted'.
    Returns 404 if request not found.
    """
    req = db.query(AdoptionRequestModel).filter(AdoptionRequestModel.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req.status = update.status

    if update.status == "approved":
        pet = db.query(PetModel).filter(PetModel.pet_id == req.pet_id).first()
        if pet:
            pet.status = "adopted"

    db.commit()
    db.refresh(req)
    return req.to_dict()


@router.put("/pets/{pet_id}/status")
def update_pet_status(pet_id: str, update: StatusUpdate, db: Session = Depends(get_db)):
    """
    Update a pet's status directly (e.g., 'available', 'adopted').
    Returns 404 if pet not found.
    """
    pet = db.query(PetModel).filter(PetModel.pet_id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    pet.status = update.status
    db.commit()
    db.refresh(pet)
    return pet.to_dict()


@router.delete("/pets/{pet_id}")
def delete_pet(pet_id: str, db: Session = Depends(get_db)):
    """
    Remove a pet record from the database.
    Cascades deletion to any associated adoption requests.
    Returns 404 if pet not found.
    """
    pet = db.query(PetModel).filter(PetModel.pet_id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    deleted_data = pet.to_dict()
    db.delete(pet)
    db.commit()
    return {"message": "Pet deleted", "pet_id": pet_id, "pet": deleted_data}


@router.get("/dashboard")
@router.get("/dashboard/")
def get_dashboard(db: Session = Depends(get_db)):
    """
    Return administrative summary dashboard metrics from database.
    """
    total_pets = db.query(PetModel).count()
    available_pets = db.query(PetModel).filter(PetModel.status == "available").count()
    total_requests = db.query(AdoptionRequestModel).count()
    pending_requests = db.query(AdoptionRequestModel).filter(AdoptionRequestModel.status == "pending").count()

    return {
        "total_pets": total_pets,
        "available_pets": available_pets,
        "total_requests": total_requests,
        "pending_requests": pending_requests
    }
