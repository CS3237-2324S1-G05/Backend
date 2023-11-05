import requests
from flask import Flask, request, jsonify
import os

ID = 1

ML_IP = '192.168.43.28'
ML_HUMAN_PRESENCE_DETECTOR_PORT = 8000
ML_CARPLATE_RECOGNITION_PORT = 8080

ML_HUMAN_PRESENCE_DETECTOR_ENDPOINT = 'ml/human'
ML_ENTRANCE_CARPLATE_RECOGNITION_ENDPOINT = 'ml/entrance'
ML_EXIT_CARPLATE_RECOGNITION_ENDPOINT = 'ml/exit'
ML_LOT_CARPLATE_RECOGNITION_ENDPOINT = 'ml/lot'

app = Flask(__name__)

UPLOAD_FOLDER_ENTRANCE = 'entrance'
app.config['CARS_FOLDER_ENTRANCE'] = UPLOAD_FOLDER_ENTRANCE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

def send_image_to_ml(port, path, id=None):
    # TODO: To be uncommented after zehou is done
    # Stub file
    # file = 'test'
    # file = open('./people/people1.jpg', 'rb')
    
    # Check if a file was included in the POST request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check if the file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format'}), 400
    
    # If image is valid
    if file:
        filename = os.path.join(app.config[upload_string], file.filename)
        file.save(filename)
        try:
            ml_url = 'http://{}:{}/{}'.format(ML_IP, port, path)
            print('Sending file to ML: {}'.format(ml_url))
            
            ml_response = None
            if path == ML_LOT_CARPLATE_RECOGNITION_ENDPOINT:
                body = {'id': id}
                ml_response = requests.post(ml_url, files={'file': file}, data=body)
            else:
                ml_response = requests.post(ml_url, files={'file': file})
            if ml_response is not None:
                return jsonify({'status': 'Successfully sent to ML: {}'.format(ml_url)}), 200
            else: 
                return jsonify({'error': 'Failed to send to ML: {}'.format(ml_url)}), 400
        except (requests.exceptions.RequestException, ValueError) as e:
            print('Error: {}'.format(e))
            return jsonify({'error': 'Did not get a response from ML: {}'.format(ml_url)}), 400
    else: 
        return jsonify({'error': 'File is invalid'}), 400
    
@app.route('/backend/human-recognition', methods=['POST'])
def handle_carpark_image():
    return send_image_to_ml(ML_HUMAN_PRESENCE_DETECTOR_PORT, ML_HUMAN_PRESENCE_DETECTOR_ENDPOINT)

@app.route('/backend/carplate-recognition/entrance', methods=['POST'])
def handle_carplate_recognition_entrance():
    return send_image_to_ml(ML_CARPLATE_RECOGNITION_PORT, ML_ENTRANCE_CARPLATE_RECOGNITION_ENDPOINT)

@app.route('/backend/carplate-recognition/exit', methods=['POST'])
def handle_carplate_recognition_exit():
    return send_image_to_ml(ML_CARPLATE_RECOGNITION_PORT, ML_EXIT_CARPLATE_RECOGNITION_ENDPOINT)

@app.route('/backend/carplate-recognition/lot', methods=['POST'])
def handle_carplate_recognition_lot():
    # TODO: Zehou to send me id in body
    data = request.json
    lot_number = data.get('id')
    return send_image_to_ml(ML_CARPLATE_RECOGNITION_PORT, ML_LOT_CARPLATE_RECOGNITION_ENDPOINT, lot_number)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port= 3237)
