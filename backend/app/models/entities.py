from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    login: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(Enum("admin", "seller", name="user_roles"), default="seller")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    branch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("branches.id"), nullable=True)
    branch: Mapped[Optional[Branch]] = relationship(back_populates="users")

    incomes: Mapped[List[Income]] = relationship(back_populates="created_by_user", cascade="all,delete")
    sales: Mapped[List[Sale]] = relationship(back_populates="seller")


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    products: Mapped[List[Product]] = relationship(back_populates="category")


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    photo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    unit: Mapped[str] = mapped_column(String(50), default="pcs")
    barcode: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    purchase_price: Mapped[float] = mapped_column(Float, default=0)
    sale_price: Mapped[float] = mapped_column(Float, default=0)
    wholesale_price: Mapped[float] = mapped_column(Float, default=0)
    limit: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    category: Mapped[Optional[Category]] = relationship(back_populates="products")
    stocks: Mapped[List[Stock]] = relationship(back_populates="product")


class Branch(Base, TimestampMixin):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    address: Mapped[Optional[str]] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    stock_items: Mapped[List[Stock]] = relationship(back_populates="branch")
    users: Mapped[List[User]] = relationship(back_populates="branch")


class Stock(Base, TimestampMixin):
    __tablename__ = "stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    branch: Mapped[Branch] = relationship(back_populates="stock_items")
    product: Mapped[Product] = relationship(back_populates="stocks")


class Income(Base, TimestampMixin):
    __tablename__ = "income"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

    created_by_user: Mapped[User] = relationship(back_populates="incomes")
    branch: Mapped[Branch] = relationship()
    items: Mapped[List[IncomeItem]] = relationship(back_populates="income", cascade="all, delete-orphan")


class IncomeItem(Base):
    __tablename__ = "income_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    income_id: Mapped[int] = mapped_column(ForeignKey("income.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    purchase_price: Mapped[float] = mapped_column(Float)
    sale_price: Mapped[float] = mapped_column(Float)

    income: Mapped[Income] = relationship(back_populates="items")


class Client(Base, TimestampMixin):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    total_debt: Mapped[float] = mapped_column(Float, default=0)

    debts: Mapped[List[Debt]] = relationship(back_populates="client")
    sales: Mapped[List[Sale]] = relationship(back_populates="client")


class Sale(Base, TimestampMixin):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    client_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clients.id"), nullable=True)
    cash: Mapped[float] = mapped_column(Float, default=0)
    kaspi: Mapped[float] = mapped_column(Float, default=0)
    credit: Mapped[float] = mapped_column(Float, default=0)
    total: Mapped[float] = mapped_column(Float, default=0)
    payment_type: Mapped[str] = mapped_column(String(50), default="cash")

    seller: Mapped[User] = relationship(back_populates="sales")
    branch: Mapped[Branch] = relationship()
    client: Mapped[Optional[Client]] = relationship(back_populates="sales")
    items: Mapped[List[SaleItem]] = relationship(back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sales_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)

    sale: Mapped[Sale] = relationship(back_populates="items")


class Debt(Base, TimestampMixin):
    __tablename__ = "debts"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    amount: Mapped[float] = mapped_column(Float)
    paid: Mapped[float] = mapped_column(Float, default=0)

    client: Mapped[Client] = relationship(back_populates="debts")


class Return(Base, TimestampMixin):
    __tablename__ = "returns"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column(Float)
    processed_by: Mapped[int] = mapped_column(ForeignKey("users.id"))


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(255))
    payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
