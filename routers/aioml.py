import os,io,shutil,pandas as pd
from fastapi import APIRouter, File, Request, Form, Response, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")
    
# GET route to display the form and any stored session message
@router.get("/aioml")
def aioml_page(request: Request,step: int = 1,message:str=''):

    return templates.TemplateResponse("projects/AllInOneMachineLearning/AIOMLapp.html", {
        "request": request,
        "step":step,
    })

# POST route to receive data from form and store in session
@router.post("/aioml/file-submit")
# async so it happens in the background
# Takes in the file and returns the head info and describe of the dataframe
async def receive_data(request: Request,file: UploadFile = File(...)):
    # define the upload directory
    upload_dir = "static/uploads"
    # check if it is there if not create
    os.makedirs(upload_dir, exist_ok=True)
    
    # make the path for the file by using upload dir and filename
    file_location = os.path.join(upload_dir, 'dataset.csv')

    # file saving open file in write binary 
    with open(file_location, "wb") as buffer:
        # copy the file to the buffer hence saving it
        shutil.copyfileobj(file.file, buffer)
    # The pointer has now reached the end of the file, so we need to seek back to the beginning
    file.file.seek(0)
    copied_file_location = 'static/uploads/copy.csv'
    request.session['copied_file_location'] = copied_file_location
    with open(copied_file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    df = pd.read_csv(copied_file_location, encoding="utf-8", engine="python")
    # We provide the df to this function 
    preview = infoAndCleaning(df)
    return JSONResponse(content=preview)

# Helper function for the aioml/file-submit route
def infoAndCleaning(df):
    # display the first 5 rows
    head_df = df.head().astype(str)
    head_html = head_df.to_html(index=False, escape=False)

    # display the info (df.info())
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    buffer.close() 
    info_html = info_str

    # display the described (df.describe())
    preview_df = df.describe().astype(str)
    describe_html = preview_df.to_html(index=False, escape=False)

    return {
        "dfHead": head_html,
        "dfInfo": info_html,
        "dfDescribe": describe_html
    }

@router.post("/aioml/missing-values")
async def viewMissingValues(request: Request):
    data = await request.json()
    print("Missing Value Process Started")
    if data['action'] == 'check':
        copied_file_location = request.session.get('copied_file_location')
        tempDf = pd.read_csv(copied_file_location, encoding="utf-8", engine="python")
        missingTable = tempDf.isnull().sum()
        missingTable = missingTable[missingTable > 0].to_dict()
        missingColumns = (list(missingTable.keys()))
        print("Missing Values Found")
        # We need to do the to_dict as otherwise it is just Pandas Series not understood by JSON, but json understands dict
        return JSONResponse(content={
            "missingTable": missingTable,
            "missingColumns": missingColumns
        })
    else:
        missingColumnData = data['columns']
        copied_file_location = request.session.get('copied_file_location')
        tempDf = pd.read_csv(copied_file_location, encoding="utf-8", engine="python")
        for i in missingColumnData.keys():
            if missingColumnData[i] == 'drop':
                tempDf.drop(columns=[i], inplace=True)
            elif missingColumnData[i] == 'mean':
                tempDf[i] = tempDf[i].fillna(tempDf[i].mean())
            elif missingColumnData[i] == 'median':
                tempDf[i] = tempDf[i].fillna(tempDf[i].median())
            elif missingColumnData[i] == 'mode':
                tempDf[i] = tempDf[i].fillna(tempDf[i].mode()[0])

        tempDf.to_csv(copied_file_location, index=False)
        print("missing values done")
        return {
            "newDFHead": tempDf.head().to_html(index=False, escape=False),
            "pathToNewFile": 'static/uploads/copy.csv'
        }

@router.get("/aioml/categorical-columns")
async def get_categorical_columns(request: Request):
    copied_file_location = request.session.get('copied_file_location')
    if not copied_file_location or not os.path.exists(copied_file_location):
        return JSONResponse(content={"error": "File not found"}, status_code=404)
    
    df = pd.read_csv(copied_file_location)
    # Select categorical columns: object, category, or boolean
    categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    return JSONResponse(content={"categorical_columns": categorical_cols})


@router.post("/aioml/one-hot-encode")
async def one_hot_encode_columns(request: Request):
    data = await request.json()
    selected_columns = data["columns"]  # List of categorical columns selected

    copied_file_location = request.session.get('copied_file_location')
    df = pd.read_csv(copied_file_location)

    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder
    # We use the column transformer to create a pipeline and then we will use the OneHotEconder

    # Here is the pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), selected_columns)
        ],
        remainder='passthrough'
    )

    # Then we fit the pipeline to the dataframe
    transformed = preprocessor.fit_transform(df)
    # transformed is a numpy array 
    
    # We need to convert it to pandas DataFrame with proper column names so...

    # We will need to get the names of all the columns (encoded and non-encoded) after the transformation

    encoded_col_names = preprocessor.named_transformers_['cat'].get_feature_names_out(selected_columns)
    # By this we get the names of the encoded columns, preprocessor will look into its transformers and  will get the 'cat' transformer
    # then we use get_feature_names_out to get names of encoded columns

    # Then we get the names of the non-encoded columns
    non_cat_cols = [col for col in df.columns if col not in selected_columns]

    # Then we combine them in a list and we will use the DataFrame constructor to create a new DF 
    final_columns = list(encoded_col_names) + non_cat_cols
    new_df = pd.DataFrame(transformed, columns=final_columns)

    new_df.to_csv(copied_file_location, index=False)

    return {
        "encodedDF": new_df.head().to_html(index=False, escape=False),
        "pathToEncodedFile": 'static/uploads/copy.csv'
    }
@router.get("/aioml/numerical-columns")
async def get_numerical_columns(request: Request):
    copied_file_location = request.session.get('copied_file_location')
    if not copied_file_location or not os.path.exists(copied_file_location):
        return JSONResponse(content={"error": "File not found"}, status_code=404)
    
    df = pd.read_csv(copied_file_location)
    numerical_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    return JSONResponse(content={"numerical_columns": numerical_cols})

from sklearn.preprocessing import RobustScaler

@router.post("/aioml/normalize")
async def normalize_columns(request: Request):
    data = await request.json()
    selected_columns = data["columns"]

    copied_file_location = request.session.get('copied_file_location')
    df = pd.read_csv(copied_file_location)

    scaler = RobustScaler()
    df[selected_columns] = scaler.fit_transform(df[selected_columns])

    df.to_csv(copied_file_location, index=False)

    return {
        "normalizedDF": df.head().to_html(index=False, escape=False),
        "pathToNormalizedFile": 'static/uploads/copy.csv'
    }
@router.get("/aioml/features")
async def get_feature_columns(request: Request):
    copied_file_location = request.session.get('copied_file_location')
    if not copied_file_location or not os.path.exists(copied_file_location):
        return JSONResponse(content={"error": "File not found"}, status_code=404)

    df = pd.read_csv(copied_file_location)
    feature_cols = df.columns.tolist()
    return JSONResponse(content={"features": feature_cols})

@router.post("/aioml/select-features")
async def select_features(request: Request):
    data = await request.json()
    selected_features = data["features"]

    copied_file_location = request.session.get('copied_file_location')
    df = pd.read_csv(copied_file_location)

    new_df = df[selected_features]
    df_path = "static/uploads/selected_features.csv"
    new_df.to_csv(df_path, index=False)

    return {
        "selectedDF": new_df.head().to_html(index=False, escape=False),
        "pathToSelected": 'static/uploads/selected_features.csv'
    }