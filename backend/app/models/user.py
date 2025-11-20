from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    login = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("admin", "employee", name="user_roles"), nullable=False)
    active = Column(Boolean, default=True)

    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    branch = relationship("Branch", back_populates="users")
