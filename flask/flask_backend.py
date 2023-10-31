import requests
import jsonify
from flask import Flask, request
import paho.mqtt.client as mqtt

# To change if needed
ML_HOST = 'localhost'
ML_PORT = 8000

MQTT_HOST = 'localhost'
MQTT_PORT = 1883
STATUS_ENTRANCE_HUMAN_PRESENCE_TOPIC = 'status/entrance/human-presence'
STATUS_ENTRANCE_CARPLATE_TOPIC = 'status/entrance/carplate'
STATUS_EXIT_CARPLATE_TOPIC = 'status/exit/carplate'
STATUS_LOT_CARPLATE_TOPIC = 'status/lot/carplate'

ML_HUMAN_ENDPOINT = 'ml/human'
ML_ENTRANCE_CARPLATE_ENDPOINT = 'ml/entrance'
ML_EXIT_CARPLATE_ENDPOINT = 'ml/exit'
ML_LOT_ENDPOINT = 'ml/lot'

app = Flask(__name__)

# Process image functions
# -----------------------
# Checks if file is of allowed file format
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

def process_image(path, id=None):
    # Check if a file was included in the POST request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    # Check if the file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format'})
    
    # If image is valid
    if file:
        try:
            ml_url = 'http://{}:{}/{}'.format(ML_HOST, ML_PORT, path)
            response = None
            if path == ML_LOT_ENDPOINT:
                # add id into body before posint request
                body = {'id': id}
                response = requests.post(ml_url, files={'file': file}, data=body)
            else:
                response = requests.post(ml_url, files={'file': file})
            if response is not None:
                is_successful = True
                message = 'Ok'
            else: 
                is_successful = False
                message = 'Failed to get carplate'
        except (requests.exceptions.RequestException, ValueError) as e:
            return False, 'Failed to get carplate'
        if is_successful:
            return jsonify({'status': message})
        else:
            return jsonify({'error': message})
    else: 
        return jsonify({'error': 'File is invalid'})
    
def publish_to_mqtt(topic, msg):
    client = mqtt.Client()
    try:
        client.connect(MQTT_HOST, MQTT_PORT)
        client.publish(topic, msg)
        client.disconnect()
        print('Message published successfully')
    except Exception as e:
        print(f'An error occurred: {e}')
        
# Receives image of carpark from ESP32
@app.route('/backend/human-recognition', methods=['POST'])
def handle_carpark_image():
    return process_image(ML_HUMAN_ENDPOINT)

@app.route('/backend/carplate-recognition/entrance', methods=['POST'])
def handle_carplate_recognition_entrance():
    return process_image(ML_ENTRANCE_CARPLATE_ENDPOINT)

@app.route('/backend/carplate-recognition/exit', methods=['POST'])
def handle_carplate_recognition_exit():
    return process_image(ML_EXIT_CARPLATE_ENDPOINT)

@app.route('/backend/carplate-recognition/lot', methods=['POST'])
def handle_carplate_recognition_lot():
    data = request.json
    lot_number = data.get('id')
    return process_image(ML_LOT_ENDPOINT, lot_number)

if __name__ == '__main__':
    app.run(port= 7000)
    