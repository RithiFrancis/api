from numpy import double
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ElectricBase(BaseModel):
    id: int
    electric_reading: float
    estimated_bill: float
    created_at: datetime

    class Config:
        from_attributes = True

class CreateElectricManagement(ElectricBase):
    pass