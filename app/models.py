from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):

    __tablename__ = 'users'
    id: Mapped[int]                 = mapped_column(primary_key=True, autoincrement=True)
    user_name: Mapped[str]          = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str]      = mapped_column(nullable=False)
    notes: Mapped[list["Note"]]     = relationship(back_populates="user", cascade="all, delete-orphan")
    created_at: Mapped[datetime]    = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime]    = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dic(self):
        return {
            "id": self.id,
            "user_name": self.name,
            "created_at": self.created_at,
            "updated_at": self.created_at
        }

class Note(Base):

    __tablename__ = 'notes'
    
    id: Mapped[int]          = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]       = mapped_column(String(100))
    content: Mapped[str]     = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[str]        = mapped_column(String(100), default='')
    user_id: Mapped[int]     = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"]     = relationship(back_populates="notes")

    #timestamp fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default= datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            'id': self.id, 
            'title': self.title, 
            'content': self.content,
            'tags': self.tags.split(",") if self.tags else [],
            'user_id': self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_deleted': self.is_deleted
        }