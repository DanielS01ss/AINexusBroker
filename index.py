from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from utils.fetch_data import fetch_data_from_database
from models.PipelineRequest import PipelineRequest
from models.OperationRequest import OperationRequest
from utils.check_db_exists import fetch_and_check_db
from utils.validate_pipeline_req import check_pipeline_request_obj
from utils.store_authorization_headers import store_authorization_token
from preprocessing_algs.microservice_calls import call_processing_endpoint
from utils.pipeline_processing import pipeline_handler
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


@app.post("/start_pipeline")
async def root(req: PipelineRequest, authorization = Header(None)):
    
    db_found = None
    fetched_data = None
    fetched_data_dict = {"name":"Daniel"}
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
        fetched_data_dict = await call_processing_endpoint(fetched_data_dict, operation)
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