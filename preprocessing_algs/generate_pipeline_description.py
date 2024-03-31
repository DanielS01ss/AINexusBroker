import pandas as pd
import requests


def generate_pipeline_description():
    print("")
    # desc = pd.read_csv("./description.csv")
    # response = requests.post("https://ollama.sedimark.work/api/chat", json={
    #     "model": "llama2",
    #     "messages": [
    #         {"role": "system", "content": 'You are a helpfull asistent that will give back a description of an AI Model based on an entry dataset, in the following format only: { "pre-processing-algorithm": { "Normalization": ["age", "creatinine_phosphokinase", "ejection_fraction", "platelets", "serum_creatinine", "serum_sodium"], "Standardization": ["age", "creatinine_phosphokinase", "ejection_fraction", "platelets", "serum_creatinine", "serum_sodium"], "Outlier Removal": ["creatinine_phosphokinase", "platelets", "serum_creatinine"],7 "KNN Imputation": ["serum_sodium"], "Log Transformation": ["creatinine_phosphokinase"], "Feature Encoding": [] }, "ml-algorithm": { "Random Forests": { "n_estimators": 100, "max_depth": null, "random_state": 42 } }'},
    #         {"role": "user", "content": f"For this dataset description: {desc.to_string()}, can you give me the JSON object with the steps that I need to take for this dataset:"}
    #     ],
    #     "stream": False
    # })

    # print(response.status_code, response.json())
    
# generate_pipeline_description()