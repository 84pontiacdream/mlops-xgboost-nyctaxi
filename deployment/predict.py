import os
import pickle

import mlflow
mlflow.tracking import MlflowClient
from flask import Flask, request, jsonify

MLFLOW_TRACKING_URI = ''
RUN_ID = ''

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

logged_model = f'runs:/{RUN_ID}/model'
# Fetch model directly from S3
# logged_model = f's3://{PATH_TO_MODEL}' #e.g 's3://mlflow-models-alexey/1/{RUN_ID}/
model = mlflow.pyfunc.load_model(logged_model)


def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    preds = model.predict(features)
    return float(preds[0])

# Create an instance of Flask application
app = Flask('duration-prediction')



@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()

    features = prepare_features(ride)
    pred = predict(features)

    result = {
        'duration': pred,
        'model_version': RUN_ID
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
