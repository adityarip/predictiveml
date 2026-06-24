from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone, timedelta

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Sensor(db.Model):
    __tablename__ = 'sensors'
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone(timedelta(hours=8))), nullable=False)
    ph_value: Mapped[float] = mapped_column(nullable=False)
    turbidity_value: Mapped[float] = mapped_column(nullable=False)
    temperature_value: Mapped[float] = mapped_column(nullable=False)
