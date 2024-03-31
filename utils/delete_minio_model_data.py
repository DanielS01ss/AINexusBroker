from minio import Minio, S3Error
from utils.extract_uuid import extract_uuid_for_model

def delete_minio_data(model_name):  
    model_uuid = extract_uuid_for_model(model_name)
    metadata_name = f"{model_uuid}_metadata.json"
    force_plot_name = f"{model_uuid}_force_plot.html"
    summary_plot = f"{model_uuid}_shap_summary_plot.png"
    minio_client = Minio(
            "127.0.0.1:9000",
            access_key="LjYOcfvfYyfYPg0ea3D3",
            secret_key="QKd4F1cgxMTLAh2MFtHYTWePbrurXNeMlf13h06D",
            secure=False  # Set to True if using HTTPS
    )


    try:
        minio_client.remove_object("ainexusmetrics", metadata_name)
        print(f"File '{metadata_name}' deleted successfully from bucket 'ainexusmetrics'.")
    except S3Error as e:
        print(f"Failed to delete file '{metadata_name}' from bucket 'ainexusmetrics': {e}")
    
    try:
        minio_client.remove_object("ainexusmodels", model_name)
        print(f"File '{model_name}' deleted successfully from bucket 'ainexusmodels'.")
    except S3Error as e:
        print(f"Failed to delete file '{model_name}' from bucket 'ainexusmodels': {e}")
    
    try:
        minio_client.remove_object("model-shap-values", force_plot_name)
        print(f"File '{force_plot_name}' deleted successfully from bucket 'model-shap-values'.")
    except S3Error as e:
        print(f"Failed to delete file '{force_plot_name}' from bucket 'model-shap-values': {e}")
    
    try:
        minio_client.remove_object("model-shap-values", summary_plot)
        print(f"File '{summary_plot}' deleted successfully from bucket 'model-shap-values'.")
    except S3Error as e:
        print(f"Failed to delete file '{summary_plot}' from bucket 'model-shap-values': {e}")