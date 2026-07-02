"""Auth router — register and login endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from database.db import patients_col
from utils.auth import hash_password, verify_password, create_access_token
from datetime import datetime

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int = 0
    phone: str = ""


@router.post("/register", summary="Register a new patient")
async def register(req: RegisterRequest):
    existing = await patients_col.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")
    patient = {
        "name": req.name,
        "email": req.email,
        "password": hash_password(req.password),
        "age": req.age,
        "phone": req.phone,
        "created_at": datetime.utcnow().isoformat(),
    }
    result = await patients_col.insert_one(patient)
    return {"message": "Registration successful", "patient_id": str(result.inserted_id)}


@router.post("/login", summary="Login and get JWT token")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    patient = await patients_col.find_one({"email": form.username})
    if not patient or not verify_password(form.password, patient["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = create_access_token({"sub": str(patient["_id"]), "email": patient["email"]})
    return {"access_token": token, "token_type": "bearer", "name": patient["name"]}
