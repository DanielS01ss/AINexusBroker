def check_pipeline_request_obj(data_dict):
    if "dataset_name" not in data_dict or "operations" not in data_dict:
        return False
    if not isinstance(data_dict["dataset_name"], str):
        return False
    if not isinstance(data_dict["operations"], list):
        return False
    return True
