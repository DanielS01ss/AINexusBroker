import httpx
import json
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from utils.store_authorization_headers import get_authorization_token

async def call_processing_endpoint(dataset, operation_obj,email):
  
    new_dataset = dataset
    if "operation_name" not in operation_obj:
        resp =  {
            "status": "Error",
            "data": new_dataset,
            "message":"Invalid request object",
            "code":400,
            "type":"stop"
        }
        return resp
    if operation_obj['operation_name'] == "Data featuring":
        
        if "columns" not in operation_obj:
            resp =  {
            "status": "Error",
            "data": new_dataset,
            "message":"Invalid request object",
            "code":400,
            }
            return resp

        if len(operation_obj["columns"]) == 0:
            
            resp =  {
                "status": "Success",
                "data": new_dataset,
                "message":"OK",
                "code":200
            }
            return resp
        
        async with httpx.AsyncClient() as client:
            data_to_send = dataset
            url = "http://localhost:8001/data-featuring"
            payload = {
                'data': data_to_send,  
                'columns': operation_obj["columns"]
            }
            payload = json.dumps(payload)
            headers = {'Content-Type': 'application/json'}
            response = await client.post(url, content=payload, headers=headers)
       
            if response.status_code == 200:
                new_dataset = response.json()
                resp = {
                "status": "Success",
                "data": new_dataset,
                "message":"OK",
                "code":200
                }
                return resp
            else:
               
                resp = {
                "status": "Error",
                "data": new_dataset,
                "message":"There was a problem while processing request!",
                "code":500
                }
                
                return resp
    elif operation_obj['operation_name'] == "Normalization":
        if "columns" not in operation_obj:
            raise HTTPException(status_code=400, detail="Request should contain columns parameter")
        if len(operation_obj["columns"]) == 0:
            resp = {
                "status": "Success",
                "data": new_dataset,
                "message":"OK",
                "code":200
                }
            return resp
        async with httpx.AsyncClient() as client:
            data_to_send = dataset
            url = "http://localhost:8001/normalization"
            payload = {
                "data": data_to_send,  
                "columns": operation_obj["columns"]
            }
            payload = json.dumps(payload)
            response = await client.post(url, content=payload, headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                new_dataset = response.json()
                resp = {
                "status": "Success",
                "data": new_dataset,
                "message":"OK",
                "code":200
                }
                return resp
            else:
                resp = {
                "status": "Error",
                "data": new_dataset,
                "message":"There was an error while processing the request!",
                "code":500
                }
                return resp

    elif operation_obj['operation_name'] == "Standardization":
        if "columns" not in operation_obj:
            raise HTTPException(status_code=400, detail="Request should contain columns parameter")
        if len(operation_obj["columns"]) == 0:
            resp = {
                "status": "Success",
                "data": new_dataset,
                "message":"OK",
                "code":200
            }
            return resp
        async with httpx.AsyncClient() as client:
            data_to_send = dataset
            
            url = "http://localhost:8001/standardization"

            payload = {
                "data": data_to_send,  
                "columns": operation_obj["columns"]
            }
            
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                new_dataset = response.json()
                resp = {
                "status": "Success",
                "data": new_dataset,
                "message":"OK",
                "code":200
                }
                return resp
            else:
                resp = {
                "status": "Error",
                "data": new_dataset,
                "message":"There was an error while processing the request!",
                "code":500
                }
                return resp
    elif operation_obj['operation_name'] == "Data imputation":
        try:
            async with httpx.AsyncClient() as client:
                data_to_send = dataset
                
                url = "http://localhost:8001/data-imputation"

                if "knn_imputation" in operation_obj and operation_obj["knn_imputation"]:
                    payload = {
                        "data": data_to_send,  
                        "knn_imputation": True,
                        "constant_value_imputation_columns": [],
                        "constant_value_imputation_values": [],
                        "regression_value_imputation_target_columns": [],
                        "regression_value_imputation_feature_columns": []
                    }
                    response = await client.post(url, json=payload)
                   

                elif "constant_value_imputation_columns" in operation_obj and len(operation_obj["constant_value_imputation_columns"]) != 0:
                    if "constant_value_imputation_values" in operation_obj:
                        data_to_send = dataset
                        url = "http://localhost:8001/data-imputation"

                        payload = {
                            "data": data_to_send,  
                            "knn_imputation": False,
                            "constant_value_imputation_columns": operation_obj["constant_value_imputation_columns"],
                            "constant_value_imputation_values": operation_obj["constant_value_imputation_values"],
                            "regression_value_imputation_target_columns": [],
                            "regression_value_imputation_feature_columns": []
                        }

                        response = await client.post(url, json=payload)

                elif "regression_value_imputation_target_columns" in operation_obj and operation_obj["regression_value_imputation_target_columns"]:
                    if "regression_value_imputation_feature_columns" in operation_obj:
                        data_to_send = dataset
                        url = "http://localhost:8001/data-imputation"

                        payload = {
                            "data": data_to_send,
                            "knn_imputation": False,
                            "constant_value_imputation_columns": [],
                            "constant_value_imputation_values": [],
                            "regression_value_imputation_target_columns": operation_obj["regression_value_imputation_target_columns"],
                            "regression_value_imputation_feature_columns": operation_obj["regression_value_imputation_feature_columns"]

                        }

                        response = await client.post(url, json=payload)

                else:
                    resp = {
                        "status":"Success",
                        "data":new_dataset,
                        "message":"OK",
                        "code":200
                    }
                    return resp
                
                if response.status_code == 200:
                    new_dataset = response.json()
                    resp = {
                    "status": "Success",
                    "data": new_dataset,
                    "message":"OK",
                    "code":200
                    }
                    return resp
                else:
                    resp = {
                    "status": "Error",
                    "data": new_dataset,
                    "message":"There was an error while processing the request!",
                    "code":500
                    }
                    return resp
        except Exception as e:
            print("There was an error:")
            print(e)
        
        
    elif operation_obj['operation_name'] == "Model Training":
        async with httpx.AsyncClient() as client:
            token = get_authorization_token()
            data_to_send = dataset
            url = "http://localhost:8086/api/models/train"
            payload = {
                 "data": data_to_send,
                 "model_name": operation_obj["ml_algorithm"],
                 "model_params": {
                    "target": operation_obj["target"]
                 },
                 "email": email
            }
            
            timeout_seconds = 600
            response = await client.post(url, json=payload,  timeout=timeout_seconds)
            
           
            if response.status_code == 200:
               
               resp = {
                "status": "Success",
                "data": new_dataset,
                "message":"OK",
                "model_name": json.loads(json.loads(response.text)["message"])["model_name"],
                "code":200
               }
               return resp
            else:
               
               resp = {
                "status": "Error",
                "data": new_dataset,
                "message": "There was an error while processing the request!",
                "code":500
               }
               return resp

    resp = {
    "status": "Success",
    "data": new_dataset,
    "message":"OK",
    "code":200
    }
    return resp
