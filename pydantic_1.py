from pydantic import BaseModel, EmailStr, AnyUrl,Field
from typing import List,Dict,Optional,Annotated


class Patient(BaseModel):
    name:str
    email: Optional[EmailStr] = "default@gmail.com"
    age:int
    linkedin : AnyUrl = "https://www.linkedin.com/in/default"
    #weight : float = Field(gt=0)#
    weight : Annotated[float, Field(title="Weight of the patient",gt=0, description="Weight must be greater than zero"),strict=True]
    height : Optional[float] = None
    marries : Field(default=False, description="Marital status of the patient")
    allergies : List[str] # not python list but pydantic list because normal list not allow to specifiy type of elements ie str
    contact_details : Dict[str,str]

patient_info = {
    "name" : "John Doe",
    "age" : 30,
    "weight" : 70.5,
    # "married" : True,
    "allergies" : ["Peanuts", "Penicillin"],
    "contact_details" : {
        "phone" : "123-456-7890",
        "email" : "abc@gmail.com"
    }
}

patient1 = Patient(**patient_info)
print(patient1)
print(patient1.name)



def printPatientDetails(patient : Patient):
    print(f"Patient Name: {patient.name}, Age: {patient.age}")
    print(f"Weight: {patient.weight} kg")    
    print(f"Allergies: {', '.join(patient.allergies)}")
    print("Contact Details:")
    for key, value in patient.contact_details.items():
        print(f"  {key.capitalize()}: {value}")


printPatientDetails(patient1)