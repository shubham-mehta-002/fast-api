from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, Dict

class Patient(BaseModel):
    name : str
    age : int  = Field(...,gt = 0)
    email : Optional[EmailStr] = "default@gmail.com"
    contact_details : Dict[str,str] 

    @model_validator()
    @classmethod
    def validate_emergency_contact(cls,model):
        if model.age > 60 and 'emergency' not in model.contact_details:
            raise ValueError("Emergency contact is required for patients over 60 years old.")
        return model

patient_info = {
    "name" : "Alice Smith",
    "age" : 25,
    "email" : "alice@hdfc.com",
    "contact_details": {
        "emergency" : "987-654-3210",
        "phone" : "123-456-7890"
    }
}

patient = Patient(**patient_info)

print(patient)