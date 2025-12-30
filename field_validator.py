from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class Patient(BaseModel):
    name : str
    age : int  = Field(...,gt = 0)
    email : Optional[EmailStr] = "default@gmail.com"

    @field_validator('email', mode="after")  # after(default)-> after type coersion, before -> before type coersion
    @classmethod
    def check_email(cls, value):
        domain = value.split("@")[-1]
        if value is None:
            return value
        if domain not in ['hdfc.com', 'gmail.com']:
            raise ValueError("Email domain must be either 'hdfc.com' or 'gmail.com'")   
        return value

    @field_validator('name')
    @classmethod
    def name(cls, value):
        return value.upper()


patient_info = {
    "name" : "Alice Smith",
    "age" : 25,
    "email" : "alice@hdfc.com"
}

patient = Patient(**patient_info)

print(patient)