from fastapi import FastAPI, Path, Query, HTTPException 
from fastapi.responses import JSONResponse
from pydantic import BaseModel, computed_field
from typing import Annotated, Literal
import json

app = FastAPI()

class Patient(BaseModel):
    
    id : Annotated[str, Field(..., description = "ID of the patient", example = "P001")]
    name : Annotated[str, Field(..., description = "Name of the patient")]
    city : Annotated[str, Field(..., description = "City of residence of the patient")]
    age : Annotated[int, Field(..., gt = 0 , lt = 120 , description = "Age of the patient")]
    gender : Annotated[Literal['Male', 'male', 'female', 'Female', 'Others'],Field(..., description = "Gender of the patient")]
    height : Annotated[float, Field(..., gt = 0 , description = "Hieght of the patient")]
    weight : Annotated[float, Field(...,gt = 0 , description = "Weight of the patient")]


    @computed_field
    @property
    def bmi(self) -> float:
        bmi = self.weight / (self.height ** 2)
        return round(bmi,2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal weight'
        elif self.bmi < 30:
            return 'Normal weight'
        else:
            return 'Obese'
        

def load_data():
    with open('patients.json', 'r') as file:
        data = json.load(file)
    return data

def save_data(data):
    with open('patients.json', 'w')as file:
        json.dump(data, file)
@app.get("/")
def hello():
    return{'message': 'Patient Management system API'}

@app.get('/about')
def about():
    return{'message': 'A fully functional API to manage your patients records'}

@app.get('/view')
def view():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id : str = Path(..., description = 'ID of the patient in the DB', example = 'P001')):
    data = load_data()

    if patient_id in data:
        return data[patient_id] 
    raise HTTPException(status_code = 404, detail = 'Patient not found')

@app.get('/sort')
def sort_patients(sort_by : str = Query(..., description = 'Sort on the basis of height, weight or bmi'), 
                  order : str = Query('asc', description = 'Sort in ascending or descending order')):
    
    valid_fields = ['height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code = 400, detail = f'Invalid field selection from {valid_fields}')

    if order not in ['asc' , 'desc']:
        raise HTTPException(status_code = 400, detail = 'Invalid order selection between asc and desc')

    data = load_data()
        
    sort_order = True if order == 'desc' else False
    sorted_data = sorted(data.values(), key = lambda x : x[sort_by], reverse = sort_order)

    return sorted_data
    

@app.post('/create')
def create_patient(patient : Patient):
    
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code = 400, detail = 'Patient with this id already exists')
    
    data[patient.id] = patient.model_dump(exclude = ['id'])

    save_data(data)

    return JSONResponse(status_code = 201, content = {'message':'Patient created successfully'})
