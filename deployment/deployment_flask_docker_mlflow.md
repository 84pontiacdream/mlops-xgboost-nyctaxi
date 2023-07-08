# Web-services: Deploying models with Flask and Docker

This sections contains the steps for retrieving and model from the MLflow model registry and deploying the model as a web-service with Flask and Docker.

## 1. Update notebook to include Scikit-Learn pipeline

The notebook is updated to use a pipeline from the Scikit-Learn library. A pipeline is a sequence of data preprocessing and modeling steps that are applied in a specific order. The pipeline in the notebook consists of two steps: 

* `DictVectorizer()` : This is a preprocessing step that converts a dictionary-like object, such as a Python dictionary, into a numerical feature matrix.

* `xgb.XGBRegressor`: An estimator step that uses the XGBoost library to build a regression model.

**->** See [xgboost_train_predict.ipynb](deployment\xgboost_train_predict.ipynb)

**->** Before funning the file record the version of Scikit-Learn and Python.

**->** Run the notebook locally (or on VM) to create new Scikit-Learn model and record the `RUN_ID`



## 2. Create predict.py file

This code is a Flask web application that serves a machine learning model for predicting the duration of a ride. Take the model from the mlflow registry Now we will load a model from the MLflow Model Registry.

This line creates an instance of Flask application:
```python 
app = Flask('duration-prediction')
```
'/predict' endpoint is defined and it will handle POST requests:
```python
@app.route('/predict', methods=['POST'])
```

Retrieves the ride information from the JSON payload of the request \
Prepares the features using the `prepare_features()` function \
Makes a prediction using the `predict()` function \
Constructs a response JSON object with the predicted duration and the model version \

```python
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
```

Main guard to ensure Flask app is only run when the script is executed directly.

Application is run with `app.run()` function, run in debug mode, listen on all network interfaces and use port 9696.

``` python
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
```

## 3. Create a virtual environment with Pipenv

Connect to the 'mlops-zoomcamp' instance and set yp a virtual environment with `Pipenv` by following these steps.

**->** Install the version of Scikit-Learn & Python that was used to create the model into the virtual environment: 

```console
pipenv install scikit-learn=={VERSION} flask gunicorn --python={VERSION}
```
Install `requests` library as a development dependency a this is only needed for test.py and not production purposes.

```console
pipenv install --dev requests
```
Enter the environment
```console
pipenv shell
```

## 3. Run predict.py file

```console
python predict.py
```

## 3. Test by running test.py file

Open new terminal and run:

```console
pipenv shell
python test.py
```
Confirm that a prediction is returned

## 4. Deploying as WGSI

We need to use gunicorn instead of flask to deploy model into production.
```console
gunicorn --bind=0.0.0.0:9696 predict:app
```
Run the test.py file again.

## 5. Create a dockerfile

A Dockerfile is a set of instructions that are used to build a Docker image. Here is the dockerfile that has been created:

```dockerfile
# Specifies the base image to use which is a lightweight version of Python 3.9.7
FROM python:3.9.7-slim

# Install pip and upgrade to latest version
RUN pip install -U pip
# Install pipenv
RUN pip install pipenv 

# Set the working directory inside the Docker container to '/app'
WORKDIR /app

# Copy these files from the current directory into '/app'
COPY [ "Pipfile", "Pipfile.lock", "./" ]

# Install dependencies specified in 'Pipfile.lock'
# '--system' flag to install as system wide 
# '--deploy' guarantees install of the exact versions of the packages
RUN pipenv install --system --deploy

# Copy files into './app'
COPY [ "predict.py", "lin_reg.bin", "./" ]

# Expose port 9696 on the container. Informs Docker that the container will listen for incoming connections on that port
EXPOSE 9696

# Sets the default command to be executed when the container starts
ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "predict:app" ]
```

Run the following command to build the Docker image based on the Dockerfile that has been created in the directory.

* **' docker build '**: The Docker command used to build an image
* **' -t ride-duration-prediction-service:v1 '**: Specifies the name and tag for the image being built. Name is 'ride-duration-prediction-service' and the tag is 'v1'
* **' . '** Specifies the directory containing the Dockerfile and other files need to create the image. This refers to the current directory.

```console
docker build -t ride-duration-prediction-service:v1 .
```

Once the build process is complete, you will have a Docker image named 'ride-duration-prediction-service' with the tag 'v1' that can be used to create Docker containers.

Run the following command to run the image:
```console
docker run -it --rm -p 9696:9696 ride-duration-prediction-service:v1
```

Then in the second CLI window, run test.py

