from pydantic import BaseModel

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- User Schemas ---
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str

# --- Note Schemas ---
class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass

class NoteResponse(NoteBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True