import requests
from flask import Flask, request, jsonify
import os

import sys
sys.path.append('../common_utils')
from logger import logger
import status_code_constants
import api_endpoint_constants
import mqtt_topic_constants
import connection_constants

app = Flask(__name__)

# TODO: To remove
UPLOAD_FOLDER = 'people'
app.config['PEOPLE_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

def send_image_to_ml(port, path, file, id=None):
    # TODO: To remove
    # file = open('./people/people1.jpg', 'rb')
    
    # Check if a file was included in the POST request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), status_code_constants.BAD_REQUEST
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), status_code_constants.BAD_REQUEST
    
    # Check if the file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format'}), status_code_constants.BAD_REQUEST
    
    # If image is valid
    if file:
        filename = os.path.join(app.config['PEOPLE_FOLDER'], file.filename)
        file.save(filename)
        fileToSend = open(filename, 'rb')
        try:
            ml_url = f'http://{connection_constants.ML_IP}:{port}/{path}'
            logger.info(f'Sending file to ML: {ml_url}')
            
            ml_response = None
            if path == mqtt_topic_constants.ML_LOT_CARPLATE_RECOGNITION_ENDPOINT:
                ml_response = requests.post(ml_url, files={'file': fileToSend, id: id})
            else:
                ml_response = requests.post(ml_url, files={'file': fileToSend})
            if ml_response is not None:
                return jsonify({'status': f'Successfully sent to ML: {ml_url}'}), status_code_constants.SUCCESS
            else: 
                return jsonify({'error': f'Did not receive response from ML: {ml_url}'}), status_code_constants.GATEWAY_TIMEOUT
        except (requests.exceptions.RequestException) as e:
            logger.error(f'Error: {e}')
            return jsonify({'error': f'[{ml_url}]: {e}'}), status_code_constants.SERVICE_UNAVAILABLE
        except (ValueError) as e:
            logger.error(f'Error: {e}')
            return jsonify({'error': f'[{ml_url}]: {e}'}), status_code_constants.BAD_REQUEST
    else: 
        return jsonify({'error': 'File is invalid'}), status_code_constants.BAD_REQUEST
    
@app.route(api_endpoint_constants.BACKEND_HUMAN_RECOGNITION_ENDPOINT, methods=['POST'])
def handle_carpark_image():
    logger.info(f'Received image from ESP32 on {api_endpoint_constants.BACKEND_HUMAN_RECOGNITION_ENDPOINT}')
    # TODO: To replace with something that can retrieve img from ESP32 request
    img = open('./people/people1.jpg', 'rb')
    # TODO: To remove
    # return jsonify({'status': f'Successfully sent to ML: {constants.ML_HUMAN_PRESENCE_DETECTOR_ENDPOINT}'}), status_code_constants.SUCCESS
    return send_image_to_ml(connection_constants.ML_HUMAN_PRESENCE_DETECTOR_PORT, mqtt_topic_constants.ML_HUMAN_PRESENCE_DETECTOR_ENDPOINT, img)

@app.route(api_endpoint_constants.BACKEND_CARPLATE_RECOGNITION_ENTRANCE_ENDPOINT, methods=['POST'])
def handle_carplate_recognition_entrance():
    logger.info(f'Received image from ESP32 on {api_endpoint_constants.BACKEND_CARPLATE_RECOGNITION_ENTRANCE_ENDPOINT}')
    # TODO: To replace with something that can retrieve img from ESP32 request
    img = open('./car/car1.jpg', 'rb')
    # TODO: To remove
    # return jsonify({'status': f'Successfully sent to ML: {constants.ML_ENTRANCE_CARPLATE_RECOGNITION_ENDPOINT}'}), status_code_constants.SUCCESS
    return send_image_to_ml(connection_constants.ML_CARPLATE_RECOGNITION_PORT, mqtt_topic_constants.ML_ENTRANCE_CARPLATE_RECOGNITION_ENDPOINT, img)

@app.route(api_endpoint_constants.BACKEND_CARPLATE_RECOGNITION_EXIT_ENDPOINT, methods=['POST'])
def handle_carplate_recognition_exit():
    logger.info(f'Received image from ESP32 on {api_endpoint_constants.BACKEND_CARPLATE_RECOGNITION_EXIT_ENDPOINT}')
    # TODO: To replace with something that can retrieve img from ESP32 request
    img = open('./car/car1.jpg', 'rb')
    # TODO: To remove
    # return jsonify({'status': f'Successfully sent to ML: {constants.ML_EXIT_CARPLATE_RECOGNITION_ENDPOINT}'}), status_code_constants.SUCCESS
    return send_image_to_ml(connection_constants.ML_CARPLATE_RECOGNITION_PORT, mqtt_topic_constants.ML_EXIT_CARPLATE_RECOGNITION_ENDPOINT, img)

@app.route(api_endpoint_constants.BACKEND_CARPLATE_RECOGNITION_LOT_ENDPOINT, methods=['POST'])
def handle_carplate_recognition_lot():
    logger.info(f'Received image from ESP32 on {api_endpoint_constants.BACKEND_CARPLATE_RECOGNITION_LOT_ENDPOINT}')
    data = request.json
    lot_number = data.get('id')
    # TODO: To replace with something that can retrieve img from ESP32 request
    img = open('./car/car1.jpg', 'rb')
    # TODO: To remove
    # return jsonify({'status': f'Successfully sent to ML: {constants.ML_LOT_CARPLATE_RECOGNITION_ENDPOINT}'}), status_code_constants.SUCCESS
    return send_image_to_ml(connection_constants.ML_CARPLATE_RECOGNITION_PORT, mqtt_topic_constants.ML_LOT_CARPLATE_RECOGNITION_ENDPOINT, img, lot_number)

if __name__ == '__main__':
    app.run(host = connection_constants.FLASK_BACKEND_IP, port = connection_constants.FLASK_BACKEND_PORT)
