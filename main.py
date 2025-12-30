from fastapi import FastAPI , Path , HTTPException, Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel , Field, computed_field
from typing import Annotated , Literal

app = FastAPI()

# Define the Patient model using Pydantic
class Patient(BaseModel):
    id: Annotated[str, Field(..., description="Unique identifier for the patient", examples=["P001", "P002"])]
    name : Annotated[str, Field(..., description="Full name of the patient", examples=["John Doe"])]
    city : Annotated[str, Field(..., description="City where the patient resides")]
    age : Annotated[int, Field(..., description="Age of the patient in years", ge=0, le=120)]
    gender : Annotated[Literal['Male', 'Female', 'Other'], Field(..., description="Gender of the patient")]
    height : Annotated[float, Field(..., description="Height of the patient in meters", ge=0)]  
    weight : Annotated[float, Field(..., description="Weight of the patient in kilograms", ge=0)]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) ->str:
        bmi_value = self.bmi
        if bmi_value < 18.5:
            return "Underweight"
        elif 18.5 <= bmi_value < 24.9:
            return "Normal weight"
        elif 25 <= bmi_value < 29.9:
            return "Overweight"
        else:
            return "Obesity"

def load_data():
    with open("./patients.json", "r") as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("./patients.json", "w") as f:
        json.dump(data, f)

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}

@app.get("/view")
def get_data():
    data = load_data()
    return data


@app.get("/view/{patient_id}")
def get_patient_by_id(patient_id : str = Path(..., description="Id of the patient to retrieve",examples=["P001"])):
    data = load_data()
    
    if patient_id in data:
        return data[patient_id]
    return HTTPException(status_code=404, detail="Patient not found")


@app.get("/sort")
def sort_patients(sort_by : str = Query(...,description="Sort on the basis of height, weight or BMI"), order :str = Query('asc',description="Ascending or descending order")):

    valid_fields = ['height', 'weight', 'bmi']
    if(sort_by not in valid_fields):
        return HTTPException(status_code=400, detail=f"Invalid sort_by field. Must be one of {valid_fields}")

    if order not in ['asc', 'desc']:
        return HTTPException(status_code=400, detail="Invalid order. Must be 'asc' or 'desc'")
    
    data = load_data()

    sorted_data = sorted(data.values(), key = lambda x : x.get(sort_by, 0), reverse = (order=='desc'))

    return sorted_data



@app.post('/create')
def create_patient(patient: Patient):
    #load existing data
    data = load_data()

    #check if patient with same id already exists
    if patient.id in data:
        return HTTPException(status_code=400, detail="Patient with this ID already exists")
    
    #add new patient
    data[patient.id] = patient.model_dump(exclude=['id'])

    # save to json file
    save_data(data)

    return JSONResponse(status_code = 201, content={
        "message" : "Patient created successfully",
        "patient" : data[patient.id]
    })

