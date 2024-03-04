import json
from utils.validate_pipeline_req import check_pipeline_request_obj
from utils.check_db_exists import fetch_and_check_db
from utils.fetch_data import fetch_data_from_database
from preprocessing_algs.microservice_calls import call_processing_endpoint

async def pipeline_handler(data_dict):
    
    db_found = None
    fetched_data = None
    stage_ready_msg = ""
    if not check_pipeline_request_obj(data_dict):
        
        error_msg = {
            "type":"Error",
            "message":"Pipeline does not meet the requirements!"
        }
        error_msg_str = json.dumps(error_msg)
        
        yield error_msg_str
        return
    if data_dict['dataset_name']:
        db_found = fetch_and_check_db(data_dict["dataset_name"])
        
    if db_found != None:
        fetched_data = await fetch_data_from_database(db_found)
    else:
        error_msg = {
            "type":"Error",
            "message":"Dataset not found!"
        }
        error_msg_str = json.dumps(error_msg)
        yield error_msg_str
        return
        
    fetched_data_dict = json.dumps(fetched_data.to_dict(orient='records'))
    fetched_data_dict = json.loads(fetched_data_dict)
    
    for i in range(len(data_dict["operations"])):
        operation = data_dict["operations"][i]
        if isinstance(fetched_data_dict, str):
            fetched_data_dict = json.loads(fetched_data_dict)
        response = await call_processing_endpoint(fetched_data_dict, operation)
        parsed_data = response["data"]
        fetched_data_dict = parsed_data
        if response["code"] == 200:
            stage_ready_msg = {
                "type":"Stage-finished",
                "stage_num":i,
                "operation_name": operation["operation_name"],
                "message": response["message"],
                "code": response["code"],
                "operation_name": data_dict["operations"][i]
            }
            stage_ready_msg = json.dumps(stage_ready_msg)
            yield stage_ready_msg
        else :
            stage_ready_msg = {
                "type":"Error",
                "stage_num":i,
                "operation_name":operation["operation_name"],
                "message": response["message"],
                "code": response["code"]
            }
            stage_ready_msg = json.dumps(stage_ready_msg)
            yield stage_ready_msg
    return