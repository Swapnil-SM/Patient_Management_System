from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json
app = FastAPI() # creating a FastAPI instance(object)

class Patient(BaseModel): #model to create a new patient

    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]


    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
        
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'


class PatientUpdate(BaseModel):  #model to update patient info
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]





def load_data():
    with open('patients.json', 'r') as f:#r-> read mode &f is just a name for the file object created when you open 'patients.json'.
        data = json.load(f)  #reads the JSON data from the file and converts it into a Python object (like a list or dictionary).

    return data

def save_data(data):
    with open('patients.json', 'w') as f: #w-> write mode means 
        json.dump(data, f) #first paramter is dictionary and second is file object means where to write the data



@app.get("/") # creating a route for GET request
def hello():
    
    return {'message':'Patient Management System API'}


@app.get("/about") # creating another route for GET request
def about():
    return {'message': 'A fully functional API to manage your patient records'}


@app.get('/view')
def view():
    data = load_data()

    return data

@app.get('/patient/{patient_id}')
def get_patient(patient_id: str=Path(..., description='ID of the patient in the DB', example='P001')): #patient_id are in string format
    data = load_data()
    patient_id = patient_id.upper()  # convert to uppercase
    if  patient_id in  data: #searching  keys in dicitionary
            return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found')



@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')): #here asc is default value and order is optional parameter as no 3 dots are used

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')
    
    data = load_data()
    sort_order = True if order=='desc' else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order) # 0 is default value if key not found  and data.values()  gives you all the values from the dictionary

    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):  #here data type of this fucn parameter is Patient model to validate incoming data

    # load existing data
    data = load_data()

    # check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    # new patient add to the database(converting patient pydantic object to dict as our data is in dict format)
    data[patient.id] = patient.model_dump(exclude=['id'])

    # save into the json file
    save_data(data)

    return JSONResponse(status_code=201, content={'message':'patient created successfully'})


@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True) #converting pydantic object to dict and exclude_unset=True means only those fields will be included in the dict which are provided in the request body not cosider the default None values..

    for key, value in updated_patient_info.items(): #.items() in Python returns both the key and value from a dictionary so you can loop through them.
        existing_patient_info[key] = value

    #existing_patient_info -> pydantic object(Patient) -> updated bmi + verdict ->pydantic object -> dict
    #Patient model  have bmi and verdict computed field . So when we create a Patient pydantic object using existing_patient_info dict , the bmi and verdict fields will be automatically computed based on the updated height and weight values.
    existing_patient_info['id'] = patient_id #adding id to the dict cuz it is required in Patient Pydantic model
    patient_pydandic_obj = Patient(**existing_patient_info)
    #-> pydantic object -> dict
    existing_patient_info = patient_pydandic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})


@app.delete('/delete/{patient_id}') #patient_id is path parameter here
def delete_patient(patient_id: str):

    # load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient deleted'})





