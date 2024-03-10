import pandas as pd
import httpx
import json
from fastapi import FastAPI, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from utils.fetch_data import fetch_data_from_database
from models.PipelineRequest import PipelineRequest
from models.OperationRequest import OperationRequest
from models.ModelDetailsRequest import ModelDetailsRequest
from utils.check_db_exists import fetch_and_check_db
from utils.validate_pipeline_req import check_pipeline_request_obj
from utils.store_authorization_headers import store_authorization_token
from utils.modify_string import modify_string
from preprocessing_algs.microservice_calls import call_processing_endpoint
from utils.pipeline_processing import pipeline_handler
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

@app.get("/model/details")
async def model_details(model_name: str = Query(..., description="The email address of the user to retrieve.")):

    modified_model_name = modify_string(model_name)
    print("The modified model name:")
    print(modified_model_name)

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

    fetched_data_dict = json.dumps(fetched_data.to_dict(orient='records'))
    pipeline_steps_status = {
        "step_details":{

        },
        "pipeline_succes":"True"
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
            "code": fetched_data_dict["code"]
        }
        fetched_data_dict = fetched_data_dict["data"]
        i = i + 1

    pipeline_steps_status = json.dumps(pipeline_steps_status)
    return pipeline_steps_status


if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0', port=8081)