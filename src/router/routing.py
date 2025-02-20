from src.models import model
from src.schema import elect_schema
from src.dbconnections.database import get_db
from fastapi import HTTPException, Depends, Request
from starlette import status
from sqlalchemy.orm import Session
from fastapi import APIRouter


router = APIRouter(
    prefix='/predictor',
    tags=['Electric_Readings']
)

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=model.CreateElectricManagement)
def create_prediction(request: Request, employee: model.CreateElectricManagement, db: Session = Depends(get_db)):  

    new_employee = elect_schema.CreateElectricManagement(**employee.dict())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee