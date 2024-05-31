import pandas as pd
import httpx
import json
from fastapi import FastAPI, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File,  UploadFile
from utils.fetch_data import fetch_data_from_database
from utils.get_pipelines_for_user import get_pipelines_for_user
from models.PipelineRequest import PipelineRequest
from models.OperationRequest import OperationRequest
from models.ModelDetailsRequest import ModelDetailsRequest
from models.PipelineSave import PipelineSave
from models.GeneratePipeline import GeneratePipeline
from models.GenerateKey import GenerateKey
from utils.save_pipeline import save_pipeline_for_user
from utils.check_db_exists import fetch_and_check_db
from utils.validate_pipeline_req import check_pipeline_request_obj
from utils.store_authorization_headers import store_authorization_token
from utils.modify_string import modify_string
from utils.delete_minio_model_data import delete_minio_data
from utils.delete_dataset_after_id import delete_dataset_after_id
from utils.fetch_generated_key import fetch_generated_key
from models.LogsRequest import LogsRequest
from preprocessing_algs.microservice_calls import call_processing_endpoint
from utils.pipeline_processing import pipeline_handler
from utils.delete_logs_for_user import delete_logs_for_user
from utils.save_logs_for_user import save_logs_for_user
from utils.get_user_logs import get_user_logs
from utils.get_columns_for_encoding import get_columns_for_encoding
from preprocessing_algs.generate_pipeline_description import generate_pipeline_description
from utils.delete_user_pipeline import delete_user_pipeline
from utils.delete_model_from_db import delete_model_from_db
from utils.check_and_fetch_minio import check_and_fetch_minio
from utils.upload_file_metadata import upload_file_metadata
from utils.generate_and_store_key import generate_and_store_key
from utils.delete_key import delete_key_for_user
from models.UploadMetadata import UploadMetadata
from io import BytesIO  # Importă BytesIO
from minio import Minio
from minio.error import S3Error
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json
from fastapi import WebSocket, WebSocketDisconnect,HTTPException
import uvicorn


app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

origin_paterns = '*'

@app.get("/model/summary_plot")
async def shap_summary(model_name:  str = Query(..., description="The email address of the user to retrieve.")):
    if len(model_name) != 0:
        async with httpx.AsyncClient() as client:
            url = f"http://localhost:8086/api/summary_plot?model_name={model_name}"
            headers = {'Content-Type': 'application/json'}
            response = await client.get(url, headers=headers)
            parsed_response = json.loads(response.text)
            return JSONResponse(content={"message": parsed_response["data"]["content"] }, status_code=200)
    else:
        return JSONResponse(content={"message": "You need to provide a model that is not empty" }, status_code=400)

@app.get("/model/force_plot")
async def shap_force_plot(model_name:  str = Query(..., description="The email address of the user to retrieve.")):
    if len(model_name) != 0:

        async with httpx.AsyncClient() as client:
            url = f"http://localhost:8086/api/force_plot?model_name={model_name}"
            headers = {'Content-Type': 'application/json'}
            response = await client.get(url, headers=headers)    
            parsed_response = json.loads(response.text)
            return JSONResponse(content={"message": parsed_response["data"]["content"] }, status_code=200)
    else:
        return JSONResponse(content={"message": "You need to provide a model that is not empty" }, status_code=400)

@app.delete("/logs")
async def delete_logs(email: str = Query(..., description="The email address of the user to retrieve.")):
    if len(email) != 0:
        delete_logs_for_user(email)
        return JSONResponse(content={"message": "Success!" }, status_code=200)
    else:
        return JSONResponse(content={"message": "You should provide an email wich is not empty!" }, status_code=400)

@app.get("/logs")
async def get_logs(email: str = Query(..., description="The email address of the user to retrieve.")):
    if len(email) != 0:
        result = await get_user_logs(email)
        return JSONResponse(content={"content": result }, status_code=200)    
    else:
        return JSONResponse(content={"message":"You have to specify email address parameter and it should not be empty!" }, status_code=400)

@app.post("/logs")
async def save_logs(req: LogsRequest):
    if len(req.email) != 0 and len(req.logs)!=0  and len(req.date)!=0 :
        save_logs_for_user(req.email, req.date, req.logs)
    else:
        return JSONResponse(content={"message":"Not all parameters have been provided" }, status_code=400)    
    return JSONResponse(content={"message":"Success" }, status_code=200)

@app.get("/model/details")
async def model_details(model_name: str = Query(..., description="The email address of the user to retrieve.")):

    modified_model_name = modify_string(model_name)


    if len(model_name) != 0:
        async with httpx.AsyncClient() as client:
            url = f"http://localhost:8086/api/model/details?model_name={modified_model_name}"
            headers = {'Content-Type': 'application/json'}
            response = await client.get(url,  headers=headers)
            response = json.loads(response.text)
            
            if response['code'] == 200:
                return JSONResponse(content={"content": response['content'] , "msg":"Success!"}, status_code=200)
            elif response['code'] == 404:
                return JSONResponse(content={"content": [], "msg":"The model was not found!"}, status_code=404)
            else:
                return JSONResponse(content={ "content":[] , "msg": "There was a problem with the request!"}, status_code=500)
    else:
            return JSONResponse(content={ "content":[] , "msg": "You need to provide a valid model"}, status_code=400)

@app.get("/models")
async def models(email: str = Query(..., description="The email address of the user to retrieve.")):
    if len(email) != 0:
        async with httpx.AsyncClient() as client:
            url = f"http://localhost:8086/api/models?email={email}"
            headers = {'Content-Type': 'application/json'}
            response = await client.get(url,  headers=headers)
            if response.status_code == 200:
                return JSONResponse(content={"models": response.text}, status_code=200)
            else:
                return JSONResponse(content={"message": "There was a problem with the request!"}, status_code=500)
    else:
        return JSONResponse(content={"message": "The email is missing!"}, status_code=400)
    
@app.delete("/model")
async def delete_model(model_name: str = Query(..., description="The email address of the user to retrieve.")):
    if len(model_name) == 0:
        return JSONResponse(content={"message": "Model name is missing"}, status_code=400)
    else:
        delete_model_from_db(model_name)
        delete_minio_data(model_name)
        return JSONResponse(content={"message": "The model was successfully deleted!"}, status_code=200)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    
    return {"filename": file.filename}

@app.post("/start_pipeline")
async def root(req: PipelineRequest):

    db_found = None
    fetched_data = None
    if req.dataset_name:
        db_found = fetch_and_check_db(req.dataset_name)
    
    if not db_found:
        return JSONResponse(content={"message": "This database does not exist!" }, status_code=400)

    if db_found[-1] != req.email and db_found[-1] != 'admin':
        return JSONResponse(content={"message": "This user is not allowed to use this dataset" }, status_code=400)    
    
    if db_found[-1] != 'admin':
        fetched_data = check_and_fetch_minio(db_found[-2])
    else:
        fetched_data = await fetch_data_from_database(db_found[-2])
        fetched_data = fetched_data.drop("id", axis=1)
    

    fetched_data_dict = json.dumps(fetched_data.to_dict(orient='records'))
    pipeline_steps_status = {
        "step_details":{

        },
        "pipeline_succes":"True",
        "trained_model": ""
    }
    i = 0
    
    for operation in req.operations:
        fetched_data_dict = await call_processing_endpoint(fetched_data_dict, operation, req.email)
        
        if fetched_data_dict["code"] ==  500:
            pipeline_steps_status["step_details"][req.operations[i]["operation_name"]] = {
            "message":fetched_data_dict["message"],
            "code": fetched_data_dict["code"]
            }
            pipeline_steps_status["pipeline_succes"] = False
            break


        pipeline_steps_status["step_details"][req.operations[i]["operation_name"]] = {
            "message":fetched_data_dict["message"],
            "code": fetched_data_dict["code"],
        }
        
        if operation["operation_name"] == "Model Training":
            pipeline_steps_status["trained_model"] = fetched_data_dict["model_name"]

        fetched_data_dict = fetched_data_dict["data"]
        i = i + 1
    
    pipeline_steps_status = json.dumps(pipeline_steps_status)
    return pipeline_steps_status

@app.delete("/dataset")
async def delete_dataset(id: int = Query(..., description="The email address of the user to retrieve.")):
    delete_dataset_after_id(id)
    return JSONResponse(content={"message": "Success!" }, status_code=200)

@app.post("/save/pipeline")
async def save_pipeline(req:PipelineSave):
    if len(req.user_email) != 0 and len(req.pipeline_name) != 0 and len(req.pipeline_data):
        save_pipeline_for_user(req.user_email, req.pipeline_name, req.pipeline_data)
        return JSONResponse(content={"message": "Success!" }, status_code=200)
    else:
         return JSONResponse(content={"message": "Empty fields!" }, status_code=400)

@app.post("/generate-pipeline")    
async def generate_pipeline(req: GeneratePipeline ):
    db_found = None
    fetched_data = None

    if req.dataset_name:
        db_found = fetch_and_check_db(req.dataset_name)

    if db_found:
        fetched_data = await fetch_data_from_database(db_found[-2])
    else:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if len(req.problem_type) == 0 or len(req.target_column) == 0:
        raise HTTPException(status_code=400, detail="Bad request")
    
  
    resp = generate_pipeline_description(fetched_data, req.problem_type, req.target_column, req.dataset_name)
    
    return JSONResponse(content={"generated_pipeline": resp }, status_code=200)

@app.get("/saved-pipelines")
async def get_saved_pipelines(user_email:  str = Query(..., description="The email address of the user to retrieve.")):
    if len(user_email) == 0:
        return JSONResponse(content={"message": "No email provided!" }, status_code=400)
    else:
        all_pipelines = await get_pipelines_for_user(user_email)
        return JSONResponse(content={"data": all_pipelines }, status_code=200)
    
@app.delete("/pipeline")
async def delete_pipeline(pipeline_name:  str = Query(..., description="The email address of the user to retrieve.")):
    if len(pipeline_name) == 0:
        return JSONResponse(content={"message": "No pipeline name provided!" }, status_code=400)
    else:
        delete_user_pipeline(pipeline_name)
        return JSONResponse(content={"message": "Success!" }, status_code=200)

@app.post("/uploadmetadata")
async def uploadmetadata(req: UploadMetadata):
    if len(req.user_email) == 0  or len(req.file_name) == 0 or len(req.tags) == 0 or len(req.authors) == 0 or len(req.publish) == 0 or len(req.description) == 0:
        return JSONResponse(content={"message": "One or more parameter is empty!" }, status_code=400)    
    else:
       await upload_file_metadata(req.user_email, req.file_name, req.tags, req.authors, req.publish, req.description)
    return JSONResponse(content={"message": "Success!" }, status_code=200)

@app.get("/columns-for-encoding")
async def uploadmetadata(dataset_name:  str = Query(..., description="The dataset that will be fetched!")):
    db_found = None
    fetched_data = None
    if dataset_name:
        db_found = fetch_and_check_db(dataset_name)
    
    if not db_found:
        return JSONResponse(content={"message": "This database does not exist!" }, status_code=400)
    if db_found[-1] != 'admin':
        fetched_data = check_and_fetch_minio(db_found[-2])
    else:
        fetched_data = await fetch_data_from_database(db_found[-2])
        fetched_data = fetched_data.drop("id", axis=1)
    
    columns_encoding = get_columns_for_encoding(fetched_data)
    
    return JSONResponse(content={"columns": columns_encoding}, status_code=200)

@app.post("/generate-key")
async def generate_key(key_data: GenerateKey):
    if len(key_data.user_email) == 0:
        raise HTTPException(status_code=400, detail="Username parameter should not be empty!")
    else:
        the_key =  generate_and_store_key(key_data.user_email) 
        return JSONResponse(content={"key": the_key }, status_code=200)

@app.delete("/generate-key")
async def delete_generated_key(key_data: str = Query(..., description="The dataset that will be fetched!")):
    if len(key_data) == 0:
        raise HTTPException(status_code=400, detail="Username parameter should not be empty!")
    else:
        delete_key_for_user(key_data) 
        return JSONResponse(content={"message": "Success!" }, status_code=200)

@app.get("/generate-key")
async def get_generated_key(key_data: str = Query(..., description="The dataset that will be fetched!")):
    if len(key_data) == 0:
        raise HTTPException(status_code=400, detail="Username parameter should not be empty!")
    else:
        fetched_keys = await fetch_generated_key(key_data)
        
    return JSONResponse(content={"keys": fetched_keys }, status_code=200) 

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    minioClient = Minio(
    "127.0.0.1:9000",
    access_key="LjYOcfvfYyfYPg0ea3D3",
    secret_key="QKd4F1cgxMTLAh2MFtHYTWePbrurXNeMlf13h06D",
    secure=False  # Setează True pentru HTTPS
    )
    try:
        
        bucket_name = "datasets"
        file_content = await file.read()
        file_stream = BytesIO(file_content)

        minioClient.put_object(
            bucket_name,
            file.filename,
            file_stream,
            length=len(file_content),
            content_type=file.content_type
        )

        return {"message": f"Fișierul '{file.filename}' a fost încărcat cu succes!"}
    except S3Error as exc:
        return {"error": str(exc)}
  
    
if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0', port=8081)

