from sqlalchemy import Column, Integer, String, Float
from .database import Base
from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    predicted_price = Column(Float)
    confidence = Column(Float)
    action = Column(String)

class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String)
    quantity = Column(Integer)
    avg_price = Column(Float)       

