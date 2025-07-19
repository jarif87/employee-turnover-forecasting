from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
import pickle

app = FastAPI()

# Mount static files for CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Load the trained CatBoost model
with open("model/catboost_model.pkl", "rb") as f:
    model = pickle.load(f)

# Define mapping dictionaries based on original LabelEncoder outputs
binary_mapping = {"No": 0, "Yes": 1}
marital_status_mapping = {
    "Div.": 0,
    "Marr.": 1,
    "NTBD": 2,
    "Sep.": 3,
    "Single": 4
}

# Home page route
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Prediction endpoint
@app.post("/predict")
async def predict(
    request: Request,
    job_role_match: str = Form(...),
    experience: float = Form(...),
    marital_status: str = Form(...),
    emp_group_b1: str = Form(...),
    location_gurgaon: str = Form(...),
    function_operation: str = Form(...),
    age: float = Form(...)
):
    try:
        # Validate string inputs
        if job_role_match not in binary_mapping:
            raise ValueError("Job Role Match must be 'Yes' or 'No'")
        if marital_status not in marital_status_mapping:
            raise ValueError("Marital Status must be one of: Div., Marr., NTBD, Sep., Single")
        if emp_group_b1 not in binary_mapping:
            raise ValueError("Emp. Group B1 must be 'Yes' or 'No'")
        if location_gurgaon not in binary_mapping:
            raise ValueError("Location Gurgaon must be 'Yes' or 'No'")
        if function_operation not in binary_mapping:
            raise ValueError("Function Operation must be 'Yes' or 'No'")

        # Convert string inputs to numeric values
        job_role_match_num = binary_mapping[job_role_match]
        marital_status_num = marital_status_mapping[marital_status]
        emp_group_b1_num = binary_mapping[emp_group_b1]
        location_gurgaon_num = binary_mapping[location_gurgaon]
        function_operation_num = binary_mapping[function_operation]

        # Prepare input data as a DataFrame
        input_data = pd.DataFrame([{
            "Job Role Match": job_role_match_num,
            "Experience (YY.MM)": experience,
            "Marital Status": marital_status_num,
            "Emp. Group_B1": emp_group_b1_num,
            "Location_Gurgaon": location_gurgaon_num,
            "Function_Operation": function_operation_num,
            "Age in YY.": age
        }])

        # Make prediction
        prediction = model.predict(input_data)[0]
        result = "Stay" if prediction == 1 else "Left"

        # Return result to the template
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "prediction": result,
                "input_data": {
                    "Job Role Match": job_role_match,
                    "Experience (YY.MM)": experience,
                    "Marital Status": marital_status,
                    "Emp. Group_B1": emp_group_b1,
                    "Location_Gurgaon": location_gurgaon,
                    "Function_Operation": function_operation,
                    "Age in YY.": age
                }
            }
        )
    except Exception as e:
        # Return error message to the template
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": str(e),
                "input_data": {
                    "Job Role Match": job_role_match,
                    "Experience (YY.MM)": experience,
                    "Marital Status": marital_status,
                    "Emp. Group_B1": emp_group_b1,
                    "Location_Gurgaon": location_gurgaon,
                    "Function_Operation": function_operation,
                    "Age in YY.": age
                }
            }
        )