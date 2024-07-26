from src import app
from src.models import Model
from flask import request
import json

# initialize the model
model = Model()
print("================================================================")

@app.route('/get_vessel_tsne', methods=['POST'])
def get_vessel_tsne():
    post_data = request.data.decode()
    post_data = json.loads(post_data)
    start_date = post_data["start_date"]
    end_date = post_data["end_date"]
    vessel_ids = post_data["vessel_ids"]
    location_ids = post_data["location_ids"]
    time_series = model.get_vessel_time_series(start_date, end_date, vessel_ids, location_ids)
    return model.get_vessel_tsne(time_series)

@app.route('/get_all_entities')
def get_all_entities():
    return model.get_all_entities()

@app.route('/get_vessel_movements', methods=['POST'])
def get_vessel_movements():
    post_data = request.data.decode()
    post_data = json.loads(post_data)
    start_date = post_data["start_date"]
    end_date = post_data["end_date"]
    vessel_ids = post_data["vessel_ids"]
    location_ids = post_data["location_ids"]
    vessel_movements = model.get_vessel_movements(start_date, end_date, vessel_ids, location_ids)
    aggregated_vessel_movements = model.get_aggregate_vessel_movements()
    return json.dumps({"vessel_movements": vessel_movements, "aggregated_vessel_movements": aggregated_vessel_movements})
