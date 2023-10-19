from flask import Flask
import os
from dotenv import load_dotenv

app = Flask(__name__)
project_folder = os.path.dirname(__file__)

load_dotenv(os.path.join(project_folder, '.env'))

env_enable = os.getenv('ENV_ENABLE');
@app.route("/")
def index():
    return f"<center><h1>Flask App deployment on AZURE {env_enable}</h1></center"

if __name__ == "__main__":
    app.run()