# database/models/users.py

from sqlalchemy import BigInteger, String, Boolean, DateTime, Float, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    __table_args__ = (
        CheckConstraint('referral_balance >= 0', name='check_balance_positive'),
        CheckConstraint('referral_total_earned >= 0', name='check_total_earned_positive'),
        CheckConstraint('referrals_count >= 0', name='check_referrals_count_positive'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(15), unique=True, nullable=True, index=True)
    nickname_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    language: Mapped[str] = mapped_column(String(5), default="ru", server_default="ru")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Реферальная система
    referrer_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    referral_balance: Mapped[float] = mapped_column(Float, default=0.0)
    referral_total_earned: Mapped[float] = mapped_column(Float, default=0.0)
    referrals_count: Mapped[int] = mapped_column(Integer, default=0)

    # ПОДДЕРЖКА (ID темы в админской группе)
    support_topic_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)