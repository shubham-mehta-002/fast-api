from fastapi import FastAPI , Path , HTTPException, Query
import json

app = FastAPI()

def load_data():
    with open("./patients.json", "r") as f:
        data = json.load(f)
    return data

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}

@app.get("/view")
def get_data():
    data = load_data()
    return data


@app.get("/view/{patient_id}")
def get_patient_by_id(patient_id : str = Path(..., description="Id of the patient to retrieve",example="P001")):
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