from src.dbconnections.database import Base
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey,Double
from sqlalchemy.orm import relationship
from datetime import datetime

class ElectricManagement(Base):
    __tablename__ = "eletricpredict2" 
    id = Column(Integer, primary_key=True, nullable=False, unique=True,autoincrement=True)
    electric_reading = Column(Double, nullable=False)
    estimated_bill = Column(Double, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())

class ElectricReadings(Base):
    __tablename__ = "electricreadings"
    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    kWh = Column(Double, nullable=False)
    kW = Column(Double, nullable=False)
    kVARh = Column(Double, nullable=False)
    kVAR = Column(Double, nullable=False)
    Time_stamp = Column(DateTime, nullable=False, default=datetime.now())