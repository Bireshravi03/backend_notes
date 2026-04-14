from sqlalchemy.orm import Session
from models import User, Note
import schemas

class UserRepository:
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(db: Session, email: str, hashed_password: str):
        db_user = User(email=email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_password(db: Session, user: User, new_hashed_password: str):
        user.hashed_password = new_hashed_password
        db.commit()
        return user

class NoteRepository:
    @staticmethod
    def get_notes(db: Session, user_id: int):
        return db.query(Note).filter(Note.owner_id == user_id).all()

    @staticmethod
    def create_note(db: Session, note: schemas.NoteCreate, user_id: int):
        db_note = Note(**note.model_dump(), owner_id=user_id)
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note

    @staticmethod
    def update_note(db: Session, note_id: int, user_id: int, note_data: schemas.NoteCreate):
        db_note = db.query(Note).filter(Note.id == note_id, Note.owner_id == user_id).first()
        if db_note:
            db_note.title = note_data.title
            db_note.content = note_data.content
            db.commit()
            db.refresh(db_note)
        return db_note

    @staticmethod
    def delete_note(db: Session, note_id: int, user_id: int):
        db_note = db.query(Note).filter(Note.id == note_id, Note.owner_id == user_id).first()
        if db_note:
            db.delete(db_note)
            db.commit()
            return True
        return False