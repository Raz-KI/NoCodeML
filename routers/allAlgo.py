

import pandas as pd
import joblib
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

# Load trained model and scaler
model = joblib.load("models\salary_prediction_LR\salary_prediction_model.pkl")
scaler = joblib.load("models\salary_prediction_LR\scaler.pkl")
model_columns = joblib.load("models\salary_prediction_LR\model_columns.pkl")

# All categories (make sure they match your training data)
GENDER_CATEGORIES = ['Male', 'Female', 'Other']
EDUCATION_CATEGORIES = ["Bachelor's", "Master's", 'PhD', "Bachelor's Degree",
       "Master's Degree", 'High School', 'phD']
JOB_CATEGORIES = ['Software Engineer', 'Data Analyst', 'Senior Manager',
       'Sales Associate', 'Director', 'Marketing Analyst',
       'Product Manager', 'Sales Manager', 'Marketing Coordinator',
       'Senior Scientist', 'Software Developer', 'HR Manager',
       'Financial Analyst', 'Project Manager', 'Customer Service Rep',
       'Operations Manager', 'Marketing Manager', 'Senior Engineer',
       'Data Entry Clerk', 'Sales Director', 'Business Analyst',
       'VP of Operations', 'IT Support', 'Recruiter', 'Financial Manager',
       'Social Media Specialist', 'Software Manager', 'Junior Developer',
       'Senior Consultant', 'Product Designer', 'CEO', 'Accountant',
       'Data Scientist', 'Marketing Specialist', 'Technical Writer',
       'HR Generalist', 'Project Engineer', 'Customer Success Rep',
       'Sales Executive', 'UX Designer', 'Operations Director',
       'Network Engineer', 'Administrative Assistant',
       'Strategy Consultant', 'Copywriter', 'Account Manager',
       'Director of Marketing', 'Help Desk Analyst',
       'Customer Service Manager', 'Business Intelligence Analyst',
       'Event Coordinator', 'VP of Finance', 'Graphic Designer',
       'UX Researcher', 'Social Media Manager', 'Director of Operations',
       'Senior Data Scientist', 'Junior Accountant',
       'Digital Marketing Manager', 'IT Manager',
       'Customer Service Representative', 'Business Development Manager',
       'Senior Financial Analyst', 'Web Developer', 'Research Director',
       'Technical Support Specialist', 'Creative Director',
       'Senior Software Engineer', 'Human Resources Director',
       'Content Marketing Manager', 'Technical Recruiter',
       'Sales Representative', 'Chief Technology Officer',
       'Junior Designer', 'Financial Advisor', 'Junior Account Manager',
       'Senior Project Manager', 'Principal Scientist',
       'Supply Chain Manager', 'Senior Marketing Manager',
       'Training Specialist', 'Research Scientist',
       'Junior Software Developer', 'Public Relations Manager',
       'Operations Analyst', 'Product Marketing Manager',
       'Senior HR Manager', 'Junior Web Developer',
       'Senior Project Coordinator', 'Chief Data Officer',
       'Digital Content Producer', 'IT Support Specialist',
       'Senior Marketing Analyst', 'Customer Success Manager',
       'Senior Graphic Designer', 'Software Project Manager',
       'Supply Chain Analyst', 'Senior Business Analyst',
       'Junior Marketing Analyst', 'Office Manager', 'Principal Engineer',
       'Junior HR Generalist', 'Senior Product Manager',
       'Junior Operations Analyst', 'Senior HR Generalist',
       'Sales Operations Manager', 'Senior Software Developer',
       'Junior Web Designer', 'Senior Training Specialist',
       'Senior Research Scientist', 'Junior Sales Representative',
       'Junior Marketing Manager', 'Junior Data Analyst',
       'Senior Product Marketing Manager', 'Junior Business Analyst',
       'Senior Sales Manager', 'Junior Marketing Specialist',
       'Junior Project Manager', 'Senior Accountant', 'Director of Sales',
       'Junior Recruiter', 'Senior Business Development Manager',
       'Senior Product Designer', 'Junior Customer Support Specialist',
       'Senior IT Support Specialist', 'Junior Financial Analyst',
       'Senior Operations Manager', 'Director of Human Resources',
       'Junior Software Engineer', 'Senior Sales Representative',
       'Director of Product Management', 'Junior Copywriter',
       'Senior Marketing Coordinator', 'Senior Human Resources Manager',
       'Junior Business Development Associate', 'Senior Account Manager',
       'Senior Researcher', 'Junior HR Coordinator',
       'Director of Finance', 'Junior Marketing Coordinator',
       'Junior Data Scientist', 'Senior Operations Analyst',
       'Senior Human Resources Coordinator', 'Senior UX Designer',
       'Junior Product Manager', 'Senior Marketing Specialist',
       'Senior IT Project Manager', 'Senior Quality Assurance Analyst',
       'Director of Sales and Marketing', 'Senior Account Executive',
       'Director of Business Development', 'Junior Social Media Manager',
       'Senior Human Resources Specialist', 'Senior Data Analyst',
       'Director of Human Capital', 'Junior Advertising Coordinator',
       'Junior UX Designer', 'Senior Marketing Director',
       'Senior IT Consultant', 'Senior Financial Advisor',
       'Junior Business Operations Analyst',
       'Junior Social Media Specialist',
       'Senior Product Development Manager', 'Junior Operations Manager',
       'Senior Software Architect', 'Junior Research Scientist',
       'Senior Financial Manager', 'Senior HR Specialist',
       'Senior Data Engineer', 'Junior Operations Coordinator',
       'Director of HR', 'Senior Operations Coordinator',
       'Junior Financial Advisor', 'Director of Engineering',
       'Software Engineer Manager', 'Back end Developer',
       'Senior Project Engineer', 'Full Stack Engineer',
       'Front end Developer', 'Developer', 'Front End Developer',
       'Director of Data Science', 'Human Resources Coordinator',
       'Junior Sales Associate', 'Human Resources Manager',
       'Juniour HR Generalist', 'Juniour HR Coordinator',
       'Digital Marketing Specialist', 'Receptionist',
       'Marketing Director', 'Social M', 'Social Media Man',
       'Delivery Driver']

# GET route to serve HTML page
@router.get("/allAlgo")
def all_algo_page(request: Request):
    return templates.TemplateResponse("projects/AllAlgo/AllAlgo.html", {
        "request": request
    })

# POST route to receive JSON input and return prediction
@router.post("/predict_salary")
async def predict_salary(request: Request):
    data = await request.json()

    # Example: data = {"Age": 35, "YearsExperience": 10, "Education Level": "Master's Degree", "Job Title": "Data Scientist", "Gender": "Male"}

    # 1️⃣ Build a one-row DataFrame with raw values
    df_input = pd.DataFrame([{
        "Age": data.get("Age"),
        "Years of Experience": data.get("YearsExperience"),
        "Education Level": data.get("Education Level"),
        "Job Title": data.get("Job Title"),
        "Gender": data.get("Gender")
    }])

    # 2️⃣ One-hot encode all categorical columns at once
    df_encoded = pd.get_dummies(df_input)
    print("Encoded input:")
    print(df_encoded)
    
    # 3️⃣ Add any missing columns (set to 0) in one shot
    missing_cols = set(model_columns) - set(df_encoded.columns)
    for col in missing_cols:
        df_encoded[col] = 0

    # 4️⃣ Reorder columns exactly as in training
    df_encoded = df_encoded[model_columns]

    # 5️⃣ Scale
    scaled_input = scaler.transform(df_encoded)

    # 6️⃣ Predict
    prediction = model.predict(scaled_input)

    return {"salary": float(prediction[0])}
