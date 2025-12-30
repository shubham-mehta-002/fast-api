from pydantic import BaseModel, EmailStr, Field, computed_field
from typing import Optional, Dict

class Patient(BaseModel):
    name : str
    weight : float = Field(...,gt=0)
    height : float = Field(...,gt=0)
    @computed_field
    @property
    def cal_bmi(self) -> float:
        bmi = round(self.weight / ((self.height/100) **2))
        return bmi

patient_info = {
    "name" : "Alice Smith",
    "age" : 25,
    "weight" : 70,
    "height" : 175
}

patient = Patient(**patient_info)

print(patient)