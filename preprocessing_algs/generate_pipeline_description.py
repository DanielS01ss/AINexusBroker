import os
import pandas as pd
import requests
from dotenv import load_dotenv
from fastapi import  HTTPException


#        AICI AI DACA VREI SA MAI INCERCI CU OLLAMA
#   
def generate_pipeline_description(the_dataset, problem_type, target_column, dataset_name):
    load_dotenv()
    desc = the_dataset.describe()
    
    api_key = os.getenv('OPENAI_API_KEY')

    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say this is a test!"}],
        "temperature": 0.7
    }

    prompt =  f'So I have a dataset called: {dataset_name} \n' + f'The target column is : {target_column} \n' + f'The problem type I am trying to solve is: {problem_type} \n' + ' \n Below I have provided the pd.describe of the dataset: \n' + f'\n {desc}'+'\n Provide the description of an AI pipeline strictly in the following JSON format and nothing else:\n'+'{\n'+'  "pre-processing-algorithm": {\n'+'    "Column Elimination": ["column1", "column2", ...],\n'+'    "Normalization": ["column1", "column2", ...],\n'+'    "Data Imputation": ["column1", "column2", ...],\n'+'    "Outlier Removal": ["column1", "column2", ...],\n'+'    "Log Transformation": ["column1", "column2",...],\n'+'    "Label Encoding": ["column1", "column2",...]\n'+' // other pre-processing steps if needed },\n'+'  "ml-algorithm": {\n'+'    "name": "algorithm_name",\n'+'    "parameters": {\n'+'      "param1": value1,\n'+'      "param2": value2\n'+'      // add additional parameters as needed\n'+'    }\n'+'  },\n'+'  "target_column": "target_column_name"\n'+'}'+'The available steps for pre-processing are:\n'+ '1. Column Elimination \n 2. Normalization \n 3. Standardization \n  4. Data Imputation \n  5. Outlier Removal  \n 6. Log Transformation \n 7. Label Encoding \n 8. Target Encoding  \n 9. One-hot Encoding'+' \n  And the machine learning algorithms available are:'+ '\n 1. Random Forest \n 2. SVM  \n 3. Linear Regression  \n 4. Logistic Regression  \n 5. Decision Trees  \n 6. Gradient Boosting Machine \n 7. KNN  \n  8. DBSCAN'
    
    # response = requests.post(url, headers=headers, json=data)
    # stored_answer = {
    #         "id": "chatcmpl-9UWD6g8r5mlGFEfqs3QMaWDKMi6fE",
    #         "object": "chat.completion",
    #         "created": 1717060684,
    #         "model": "gpt-3.5-turbo-0125",
    #         "choices": [
    #             {
    #                 "index": 0,
    #                 "message": {
    #                     "role": "assistant",
    #                     "content": "This is a test!"
    #                 },
    #                 "logprobs": 0,
    #                 "finish_reason": "stop"
    #             }
    #         ],
    #         "usage": {
    #             "prompt_tokens": 13,
    #             "completion_tokens": 5,
    #             "total_tokens": 18
    #         },
    #         "system_fingerprint": 0
    #     }
    
    # This is how we extract the answer from chatgpt when we recieve the answer in a format like json
    # stored_answer = response.json()
    # extract_the_answer = stored_answer["choices"][0]["message"]["content"]
    return {
        "pre-processing-algorithm": {
            "Column Elimination": ["id"],
            "Data Imputation": ["creatinine_phosphokinase", "platelets", "serum_creatinine", "serum_sodium"],
            "Outlier Removal": ["creatinine_phosphokinase"],
            "Normalization": ["creatinine_phosphokinase", "platelets", "serum_creatinine", "serum_sodium", "time"],
            "Label Encoding": ["sex", "smoking", "anaemia", "diabetes", "high_blood_pressure"]
        },
        "ml-algorithm": {
            "name": "Random Forest",
            "parameters": {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 2,
            "min_samples_leaf": 1
            }
        },
        "target_column": "death_event"
        }

    # try:
        
        # response = requests.post("https://ollama.sedimark.work/api/chat", json={
        # "model": "llama2",
        # "messages": [
        #     {
        #         "role": "system",
        #         "content": (
        #             'You are a helpful assistant that assists in building AI models based on an entry dataset and the specified problem type. '
        #             'The dataset description provided below is generated using pd.describe(), which includes statistical summaries of the dataset. '
        #             'Your task is to: '
        #             '1. Select the most appropriate pre-processing algorithms from the following list based on the dataset summary: '
        #             'Column Elimination, Normalization, Data Imputation, Outlier Removal, Log Transformation, Feature Encoding. '
        #             '2. For each pre-processing algorithm, specify the columns it should be applied to. '
        #             '3. Select the most suitable machine learning algorithm from this list based on the type of problem (e.g., classification, regression): '
        #             'Random Forest, SVM, Linear Regression, Logistic Regression, Decision Trees, Gradient Boosting Machine, KNN, DBSCAN. '
        #             f'4. Use the specified target column for the prediction task: {target_column}. Do not eliminate this column or use it in any pre-processing steps. '
        #             '5. Ensure that no column recommended for pre-processing is also recommended for elimination. '
        #             '6. Do not eliminate the target column or use any column that is recommended for elimination in any pre-processing steps. '
        #             '7. When providing parameters for the selected machine learning algorithm, ensure they are formatted as key-value pairs, for example: "random_state": 42, "n_estimators": 100. '
        #             '8. Ignore statistical summary rows such as "mean", "std", "min", "max", "25%", "50%", "75%", and "count" when selecting columns for pre-processing or elimination. '
        #             '9. Always recommend the removal of the "id" column during pre-processing. '
        #             'Provide the description strictly in the following JSON format and nothing else:\n'
        #             '{\n'
        #             '  "pre-processing-algorithm": {\n'
        #             '    "Column Elimination": ["column1", "column2"],\n'
        #             '    "Normalization": ["column1", "column2"],\n'
        #             '    "Data Imputation": ["column1", "column2"],\n'
        #             '    "Outlier Removal": ["column1", "column2"],\n'
        #             '    "Log Transformation": ["column1", "column2"],\n'
        #             '    "Feature Encoding": ["column1", "column2"]\n'
        #             '  },\n'
        #             '  "ml-algorithm": {\n'
        #             '    "name": "algorithm_name",\n'
        #             '    "parameters": {\n'
        #             '      "param1": value1,\n'
        #             '      "param2": value2\n'
        #             '      // add additional parameters as needed\n'
        #             '    }\n'
        #             '  },\n'
        #             '  "target_column": "target_column_name"\n'
        #             '}'
        #         )
        #     },
        #     {
        #         "role": "user",
        #         "content": (
        #             f'For this dataset description: {desc} and the specified problem type {problem_type}, provide the JSON object with the necessary pre-processing steps, machine learning algorithm, and specify the target column for the prediction task. '
        #             f'The target column is: {target_column}. Do not eliminate this column or use it in any pre-processing steps. '
        #             'Select the most appropriate pre-processing algorithms and specify the columns they should be applied to based on the dataset summary and the problem type. '
        #             'Do not suggest eliminating any column that is also recommended for pre-processing. '
        #             'Do not eliminate the target column or use any column that is recommended for elimination in any pre-processing steps. '
        #             'When providing parameters for the selected machine learning algorithm, ensure they are formatted as key-value pairs, for example: "random_state": 42, "n_estimators": 100. '
        #             'Ignore statistical summary rows such as "mean", "std", "min", "max", "25%", "50%", "75%", and "count" when selecting columns for pre-processing or elimination. '
        #             'Respond with only the JSON object and no additional information.'
        #             'Always recommend the removal of the "id" column during pre-processing if needed'
        #         )
        #     }
        #     ],
        #     "stream": False
        # })
    # except:     
    #         return {
    #             "pre-processing-algorithm":{
    #                 "Column Elimination" : ["id"],
    #                 "Normalization":[],
    #                 "Data Imputation": [],
    #                 "Outlier Removal":[],
    #                 "Log Transformation":[],
    #                 "Feature Encoding": []
    #             },
    #             "ml-algorithm":{
    #                 "name":"Random Forest",
    #                 "parameters":{
    #                     "max_depth":50,
    #                     "n_estimators":10
    #                 }
    #             }
    #         }
        
    # print(response.status_code)
    # if response.status_code == 200:
            
    #         the_response = response.json()["message"]["content"]
    #         return the_response
    # else:
            
    #         return {
    #             "pre-processing-algorithm":{
    #                 "Column Elimination" : ["anaemia"],
    #                 "Normalization":[],
    #                 "Data Imputation": ["anaemia"],
    #                 "Outlier Removal":[],
    #                 "Log Transformation":[],
    #                 "Feature Encoding": []
    #             },
    #             "ml-algorithm":{
    #                 "name":"Random Forest",
    #                 "parameters":{
    #                     "max_depth":50,
    #                     "n_estimators":10
    #                 }
    #             }
    #         }
        



#  response = requests.post("https://ollama.sedimark.work/api/chat", json={
#         "model": "llama2",
#         "messages": [
#             {"role": "system", "content": 'You are a helpfull asistent that will give back a description of an AI Model based on an entry dataset, in the following format only: { "pre-processing-algorithm": { "Normalization": ["age", "creatinine_phosphokinase", "ejection_fraction", "platelets", "serum_creatinine", "serum_sodium"], "Standardization": ["age", "creatinine_phosphokinase", "ejection_fraction", "platelets", "serum_creatinine", "serum_sodium"], "Outlier Removal": ["creatinine_phosphokinase", "platelets", "serum_creatinine"],7 "KNN Imputation": ["serum_sodium"], "Log Transformation": ["creatinine_phosphokinase"], "Feature Encoding": [] }, "ml-algorithm": { "Random Forests": { "n_estimators": 100, "max_depth": null, "random_state": 42 } }'},
#             {"role": "user", "content": f"For this dataset description: {desc.to_string()}, can you give me the JSON object with the steps that I need to take for this dataset and no other information please:"}
#         ],
#         "stream": False
#     })

    
