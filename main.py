from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional

app = FastAPI()

# --------------------- Patient Model ---------------------
class Patient(BaseModel):
    id: Annotated[str, Field(..., description="Unique identifier for the patient", examples=["P001", "P002"])]
    name: Annotated[str, Field(..., description="Full name of the patient", examples=["John Doe"])]
    city: Annotated[str, Field(..., description="City where the patient resides")]
    age: Annotated[int, Field(..., description="Age of the patient in years", ge=0, le=120)]
    gender: Annotated[Literal['Male', 'Female', 'Other'], Field(..., description="Gender of the patient")]
    height: Annotated[float, Field(..., description="Height of the patient in meters", ge=0)]
    weight: Annotated[float, Field(..., description="Weight of the patient in kilograms", ge=0)]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        bmi_value = self.bmi
        if bmi_value < 18.5:
            return "Underweight"
        elif bmi_value < 25:
            return "Normal weight"
        elif bmi_value < 30:
            return "Overweight"
        else:
            return "Obesity"

# --------------------- Patient Update Model ---------------------
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['Male', 'Female', 'Other']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

    @computed_field
    @property
    def bmi(self) -> Optional[float]:
        # Safe calculation if height or weight is missing
        if self.weight is None or self.height is None:
            return None
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> Optional[str]:
        bmi_value = self.bmi
        if bmi_value is None:
            return None
        if bmi_value < 18.5:
            return "Underweight"
        elif bmi_value < 25:
            return "Normal weight"
        elif bmi_value < 30:
            return "Overweight"
        else:
            return "Obesity"

# --------------------- Helper Functions ---------------------
def load_data():
    try:
        with open("./patients.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open("./patients.json", "w") as f:
        json.dump(data, f)

# --------------------- Routes ---------------------
@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}

@app.get("/view")
def get_data():
    data = load_data()
    return data

@app.get("/view/{patient_id}")
def get_patient_by_id(patient_id: str = Path(..., description="Id of the patient to retrieve", examples=["P001"])):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description="Sort on the basis of height, weight or bmi"),
    order: str = Query('asc', description="Ascending or descending order")
):
    valid_fields = ['height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by field. Must be one of {valid_fields}")
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid order. Must be 'asc' or 'desc'")

    data = load_data()
    sorted_data = sorted(
        data.values(),
        key=lambda x: x.get(sort_by, 0),
        reverse=(order == 'desc')
    )
    return sorted_data

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    data[patient.id] = patient.model_dump(exclude=['id'])
    save_data(data)
    return JSONResponse(status_code=201, content={
        "message": "Patient created successfully",
        "patient": data[patient.id]
    })

@app.put("/update/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    existing_patient_data = data[patient_id]
    update_data = patient_update.model_dump(exclude_unset=True)  # only provided fields
    for key, value in update_data.items():
        existing_patient_data[key] = value

    existing_patient_data['id'] = patient_id
    patient_pydantic_object = Patient(**existing_patient_data)
    patient_dict = patient_pydantic_object.model_dump(exclude=['id'])

    data[patient_id] = patient_dict
    save_data(data)

    return JSONResponse(status_code=200, content={
        "message": "Patient updated successfully",
        "patient": data[patient_id]
    })
