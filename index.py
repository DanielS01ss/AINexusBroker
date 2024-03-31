import pandas as pd
import httpx
import json
from fastapi import FastAPI, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from utils.fetch_data import fetch_data_from_database
from utils.get_pipelines_for_user import get_pipelines_for_user
from models.PipelineRequest import PipelineRequest
from models.OperationRequest import OperationRequest
from models.ModelDetailsRequest import ModelDetailsRequest
from models.PipelineSave import PipelineSave
from models.GeneratePipeline import GeneratePipeline
from utils.save_pipeline import save_pipeline_for_user
from utils.check_db_exists import fetch_and_check_db
from utils.validate_pipeline_req import check_pipeline_request_obj
from utils.store_authorization_headers import store_authorization_token
from utils.modify_string import modify_string
from utils.delete_minio_model_data import delete_minio_data
from models.LogsRequest import LogsRequest
from preprocessing_algs.microservice_calls import call_processing_endpoint
from utils.pipeline_processing import pipeline_handler
from utils.delete_logs_for_user import delete_logs_for_user
from utils.save_logs_for_user import save_logs_for_user
from utils.get_user_logs import get_user_logs
from preprocessing_algs.generate_pipeline_description import generate_pipeline_description
from utils.delete_user_pipeline import delete_user_pipeline
from utils.delete_model_from_db import delete_model_from_db
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

@app.post("/start_pipeline")
async def root(req: PipelineRequest):

    db_found = None
    fetched_data = None
    if req.dataset_name:
        db_found = fetch_and_check_db(req.dataset_name)

    if db_found:
        fetched_data = await fetch_data_from_database(db_found)
    else:
        raise HTTPException(status_code=404, detail="Dataset not found")

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
        fetched_data = await fetch_data_from_database(db_found)
    else:
        raise HTTPException(status_code=404, detail="Dataset not found")

    generate_pipeline_description(fetched_data)
    
    return JSONResponse(content={"message": "Success!" }, status_code=200)

@app.get("/saved-pipelines")
async def get_saved_pipelines(user_email:  str = Query(..., description="The email address of the user to retrieve.")):
    if len(user_email) == 0:
        return JSONResponse(content={"message": "No email provided!" }, status_code=400)
    else :
        all_pipelines = await get_pipelines_for_user(user_email)
        return JSONResponse(content={"data": all_pipelines }, status_code=200)
    
@app.delete("/pipeline")
async def delete_pipeline(pipeline_name:  str = Query(..., description="The email address of the user to retrieve.")):
    if len(pipeline_name) == 0:
        return JSONResponse(content={"message": "No pipeline name provided!" }, status_code=400)
    else:
        delete_user_pipeline(pipeline_name)
        return JSONResponse(content={"message": "Success!" }, status_code=200)
    
    
if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0', port=8081)