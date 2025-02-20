from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import numpy as np
import tensorflow as tf
import uvicorn
from datetime import datetime
from src.schema import elect_schema
from src.dbconnections.database import engine, SessionLocal, get_db
from src.schema.elect_schema import ElectricManagement, ElectricReadings
from sqlalchemy import extract, func

# Initialize FastAPI App
app = FastAPI(
    title="ML Model Deployment",
    description="A FastAPI application to serve an ML model",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    elect_schema.Base.metadata.create_all(bind=engine)  # Create tables within the database

# Load ML Model
MODEL_PATH = "lstm_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

# Define Output Data Structure
class PredictionResponse(BaseModel):
    predictions: list[float]

# Root route
@app.get("/")
def root():
    return {"message": "Welcome to the ML Model API"}

# Prediction Route
@app.post("/predict", response_model=PredictionResponse)
def predict(db: Session = Depends(get_db)):
    try:
        # Fetch the kW values grouped by month and year, summing them
        readings = (
            db.query(
                extract('year', ElectricReadings.Time_stamp).label('year'),
                extract('month', ElectricReadings.Time_stamp).label('month'),
                func.sum(ElectricReadings.kW).label('total_kw')
            )
            .group_by(extract('year', ElectricReadings.Time_stamp), extract('month', ElectricReadings.Time_stamp))
            .order_by(extract('year', ElectricReadings.Time_stamp).desc(), extract('month', ElectricReadings.Time_stamp).desc())
            .all()
        )

        # Extract the summed kW values
        monthly_kw_values = [reading.total_kw for reading in readings]

        # Prepare the input data for the model (the summed kW values)
        input_data = np.array(monthly_kw_values).reshape(1, -1)  # Reshaping for model input
        predictions_list = []

        # Define the TNEB tariff structure
        def calculate_bill(kWh):
            if kWh <= 100:
                return 0.00
            elif 100 < kWh <= 200:
                return (kWh - 100) * 3.00
            elif 200 < kWh <= 500:
                return (100 * 3.00) + (kWh - 200) * 4.50
            else:
                return (100 * 3.00) + (300 * 4.50) + (kWh - 500) * 6.00

        # Make the prediction with the entire dataset
        predictions = model.predict(input_data)
        predictions_list.extend(predictions.flatten().tolist())  # Flatten the predictions and store them

        # For each prediction, calculate energy consumption (in kWh) and estimated bill
        for prediction in predictions.flatten():
            # Convert prediction to native Python float before inserting
            prediction_value = float(prediction)
            
            # Calculate kWh based on predicted kW and assumed hours
            kWhvalue = prediction_value * 24  # Assuming 24 hours per day

            # Calculate the estimated bill based on the kWh
            estimated_bill = calculate_bill(kWhvalue)

            # Convert estimated bill to native Python float
            estimated_bill_value = float(estimated_bill)

            # Insert predicted reading and calculated bill into the database
            new_entry = ElectricManagement(
                electric_reading=round(prediction_value, 2),
                estimated_bill=round(estimated_bill_value, 2),
                created_at=datetime.now()
            )
            db.add(new_entry)

        db.commit()

        return PredictionResponse(predictions=predictions_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
