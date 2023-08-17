from src import app
from src.models import Model
from flask import request
import json

# initialize the model
model = Model()
print("================================================================")


@app.route('/get')
def _get():
    return "Get"


@app.route('/get_example_data')
def _get_example_data():
    return model.get_example_data()


@app.route('/modify_example_data', methods=['POST'])
def _modify_example_data():
    post_data = request.data.decode()
    post_data = json.loads(post_data)
    value = post_data["example"]
    if not isinstance(value, (int)):
        return ""
    model.modify_example_data(value)
    return model.get_example_data()
