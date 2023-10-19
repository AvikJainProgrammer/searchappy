from flask import Flask, jsonify, request
import json
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)

project_folder = os.path.dirname(__file__)

load_dotenv(os.path.join(project_folder, '.env'))

ENV_ENABLE = os.getenv('ENV_ENABLE');
API_VERSION = os.getenv('API_VERSION')
API_KEY = os.getenv('API_KEY')
OPENAI_ENGINE = os.getenv('OPENAI_ENGINE')
OPENAI_URL = os.getenv('OPENAI_URL')
COGNITIVE_SEARCH_ENDPOINT = os.getenv('COGNITIVE_SEARCH_ENDPOINT')
COGNITIVE_SEARCH_KEY = os.getenv('COGNITIVE_SEARCH_KEY')
COGNITIVE_SEARCH_INDEX_NAME = os.getenv('COGNITIVE_SEARCH_INDEX_NAME')

@app.route("/")
def index():
    return f"<center><h1>Flask App deployment on AZURE {ENV_ENABLE}, {API_VERSION}, {API_KEY}, {OPENAI_ENGINE}, {OPENAI_URL}, {COGNITIVE_SEARCH_ENDPOINT}, {COGNITIVE_SEARCH_KEY}, {COGNITIVE_SEARCH_INDEX_NAME}</h1></center"

@app.route("/get_response", methods=["POST"])
def get_response():
    openai_url = os.getenv('OPENAI_URL');
    url = openai_url

    headers = {
        "Content-Type": "application/json",
        "api-key": os.getenv('API_KEY'),
    }
    user_input = request.get_json().get("message")

    body = {
        "dataSources": [
            {
                "type": "AzureCognitiveSearch",
                "parameters": {
                    "endpoint": os.getenv('COGNITIVE_SEARCH_ENDPOINT'),
                    "key": os.getenv('COGNITIVE_SEARCH_KEY'),
                    "indexName": os.getenv('COGNITIVE_SEARCH_INDEX_NAME'),
                    "semanticConfiguration": None,
                    "queryType": "simple",
                    "fieldsMapping": {
                        "contentFieldsSeparator": "\n",
                        "contentFields": ["content"],
                        "filepathField": None,
                        "titleField": None,
                        "urlField": "url",
                        "vectorFields": [],
                    },
                    "inScope": True,
                    "roleInformation": "You are an AI assistant that helps people find information. answer only if there is relevent documents is there",
                    "filter": None,
                    "embeddingEndpoint": None,
                    "embeddingKey": None,
                },
            }
        ],
        "messages": [{"role": "user", "content": user_input}],
        "deployment": os.getenv('OPENAI_ENGINE'),
        "temperature": 0,
        "top_p": 1,
        "max_tokens": 800,
        "stop": None,
        "stream": False,
    }

    response = requests.post(url, headers=headers, json=body)

    json_response = response.json()

    message = json_response["choices"][0]["messages"][1]["content"]

    tool_message_content = json_response["choices"][0]["messages"][0]["content"]

    # Converting the content string to a dictionary

    tool_message_content_dict = json.loads(tool_message_content)

    # Extracting the 'citations' field if present
    url2 = ""
    if "citations" in tool_message_content_dict:
        citations = tool_message_content_dict["citations"]

        # Extracting the URL from the first citation if present

        if citations:
            first_citation = citations[0]

            if "url" in first_citation:
                url2 = first_citation["url"]

                # print(url2)

            else:
                print("No URL found in the first citation")

        else:
            print("No citations found")
    else:
        print("No 'citations' field found in the tool message content")

    # print(message)
    url2 = url2.replace("/chatbot/", "/originaldocuments/") # change citiation url to original documents url 
    return jsonify({"assistant_content": message + url2})

if __name__ == "__main__":
    app.run()