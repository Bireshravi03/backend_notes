from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import engine, get_db
from repository import UserRepository, NoteRepository
from service import AuthService, get_current_user

# Automatically create the database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure API Backend")

# Configure CORS so the React frontend can communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Update this if React runs on a different port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTHENTICATION ROUTES ---

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = UserRepository.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = AuthService.get_password_hash(user.password)
    return UserRepository.create_user(db=db, name=user.name, email=user.email, hashed_password=hashed_pwd)

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 defaults to looking for a 'username' field, which we use for the email
    user = UserRepository.get_user_by_email(db, email=form_data.username)
    if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = AuthService.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/reset-password")
def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    user = UserRepository.get_user_by_email(db, email=request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_hashed = AuthService.get_password_hash(request.new_password)
    UserRepository.update_password(db, user, new_hashed)
    return {"message": "Password updated successfully"}


# --- CRUD ROUTES FOR NOTES ---

@app.post("/notes/", response_model=schemas.NoteResponse)
def create_note(
    note: schemas.NoteCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return NoteRepository.create_note(db=db, note=note, user_id=current_user.id)

@app.get("/notes/", response_model=List[schemas.NoteResponse])
def read_notes(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return NoteRepository.get_notes(db=db, user_id=current_user.id)

@app.put("/notes/{note_id}", response_model=schemas.NoteResponse)
def update_note(
    note_id: int, 
    note: schemas.NoteCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    updated_note = NoteRepository.update_note(db=db, note_id=note_id, user_id=current_user.id, note_data=note)
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note

@app.delete("/notes/{note_id}")
def delete_note(
    note_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    success = NoteRepository.delete_note(db=db, note_id=note_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    # This tells Python to run the server on localhost port 8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)