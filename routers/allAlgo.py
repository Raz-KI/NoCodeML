
import pickle
import pandas as pd
import joblib
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import os

render_path = "/opt/render/project/src"

router = APIRouter()

templates = Jinja2Templates(directory="templates")

model = joblib.load("models/salary_prediction_LR/salary_prediction_model.pkl")
scaler = joblib.load("models/salary_prediction_LR/scaler.pkl")
model_columns = joblib.load("models/salary_prediction_LR/model_columns.pkl")

    

# Comment this if you are running locally
model = joblib.load(render_path+"/models/salary_prediction_LR/salary_prediction_model.pkl")
scaler = joblib.load(render_path+"/models/salary_prediction_LR/scaler.pkl")
model_columns = joblib.load(render_path+"/models/salary_prediction_LR/model_columns.pkl")

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

    df_input = pd.DataFrame([{
        "Age": data.get("Age"),
        "Years of Experience": data.get("YearsExperience"),
        "Education Level": data.get("Education Level"),
        "Job Title": data.get("Job Title"),
        "Gender": data.get("Gender")
    }])

    # One hot encode input
    df_encoded = pd.get_dummies(df_input)
    print("Encoded input:")
    print(df_encoded)

    # Since we one hot encoded the model and input means there are many columns that are not present in the input
    # We need to add those columns with 0 values to the input DataFrame
    missing_cols = list(set(model_columns) - set(df_encoded.columns))

    # Create a DataFrame with the missing columns all set to 0
    missing_df = pd.DataFrame(0, index=df_encoded.index, columns=missing_cols)

    # Concatenate in one go
    df_encoded = pd.concat([df_encoded, missing_df], axis=1)
    df_encoded = df_encoded[model_columns]


    # REORDER COLUMNS
    df_encoded = df_encoded[model_columns]

    # Scale
    scaled_input = scaler.transform(df_encoded)

    #  Predict
    prediction = model.predict(scaled_input)

    return {"salary": float(prediction[0])}
