import paho.mqtt.client as mqtt
from datetime import datetime, timezone
import math
import requests

import sys
sys.path.append('../common_utils')
from logger import logger
import api_endpoint_constants
import mqtt_topic_constants
import connection_constants
import status_code_constants

def publish_to_topic(topic, msg, fn_name):
    logger.info(f'{fn_name}: Publish to {topic}, message: {msg}')
    client.publish(topic, msg)

def handle_gantry_event(topic, msg):
    fn_name = 'handle_gantry_event'
    topic_levels = topic.split('/')
    gantry_name = topic_levels[-1]
    try:
        if gantry_name == 'entrance':
            handle_car_at_entrance()
        elif gantry_name == 'exit':
            handle_car_at_exit()
        else:
            logger.error(f'{fn_name}: Unknown gantry name: {gantry_name}')
    except Exception as e:
        logger.error(f'{fn_name}: {e}')

def handle_car_at_entrance():
    fn_name = 'handle_car_at_entrance'
    # Inform ESP32 to take photo of carpark, gantry entrance
    publish_to_topic(mqtt_topic_constants.CAM_CARPARK_TOPIC, '1', fn_name)
    publish_to_topic(mqtt_topic_constants.CAM_GANTRY_ENTRANCE_TOPIC, '1', fn_name)
    
    # Stub
    response = requests.post('http://{}:{}/{}'.format('localhost', 7000, 'backend/human-recognition'))
    # Stub
    response = requests.post('http://{}:{}/{}'.format('localhost', 7000, 'backend/carplate-recognition/entrance'))
    
    # Inform gantry the nearest lot (Return str(id) or str(None))
    nearest_available_lot = get_data_from_db(api_endpoint_constants.DB_GET_NEAREST_AVAILABLE_LOT_ENDPOINT)
    publish_to_topic(mqtt_topic_constants.STATUS_ENTRANCE_NEAREST_LOT_TOPIC, nearest_available_lot, fn_name)
    
def handle_car_at_exit():
    fn_name = 'handle_car_at_exit'
    # Inform ESP32 to take photo of gantry entrance
    publish_to_topic(mqtt_topic_constants.CAM_GANTRY_EXIT_TOPIC, '1', fn_name)
    
    # Stub
    response = requests.post('http://{}:{}/{}'.format('localhost', 7000, 'backend/carplate-recognition/exit'))
        
def handle_lot_event(topic, msg):
    fn_name = 'handle_lot_event'
    topic_levels = topic.split('/')
    event_type = topic_levels[-2]  # Get the event type (park or leave)
    try:
        lot_number = int(topic_levels[-1])
    except ValueError:
        logger.error(f'{fn_name}: Invalid lot number: {topic_levels[-1]}')
    if lot_number >= number_of_lots:
        logger.error(f'{fn_name}: Unknown lot number: {lot_number}')
    
    try:
        if event_type == 'park':
            handle_car_park_lot(lot_number)
        elif event_type == 'leave':
            handle_car_leave_lot(lot_number)
        else:
            logger.error(f'{fn_name}: Unknown event type: {event_type}')
    except Exception as e:
        logger.error(f'{fn_name}: {e}')
        
def update_lot_availability(lot_number, is_available, fn_name):
    fn_name = 'update_lot_availability'
    path = api_endpoint_constants.DB_UPDATE_LOT_AVAILABILITY_ENDPOINT
    data: {
        'lotId': lot_number,
        'isAvailable': is_available
    }
    post_data_to_db(path, data)
    
    # Update entrance with latest number of available lots
    number_of_available_lots = get_data_from_db(api_endpoint_constants.DB_GET_NUMBER_OF_AVAILABLE_LOTS_ENDPOINT)
    publish_to_topic(mqtt_topic_constants.STATUS_ENTRANCE_NUMBER_OF_AVAILABLE_LOTS_TOPIC, number_of_available_lots, fn_name)

def handle_car_park_lot(lot_number):
    fn_name = 'handle_car_park_lot'
    # Check if lot is available (lot availability should be true)
    lot_availability = get_data_from_db(api_endpoint_constants.DB_GET_LOT_AVAILABILITY_ENDPOINT, lot_number)
    
    if lot_availability == True:
        update_lot_availability(lot_number, False, fn_name)
            
        # Request ESP32 to take photo of lot/carplate
        publish_to_topic(mqtt_topic_constants.CAM_LOT_TOPIC + str(lot_number), '1', fn_name)

        # Stub    
        url = 'http://{}:{}/{}'.format('localhost', 7000, 'backend/carplate-recognition/lot')
        data = {'id': '1'}
        response = requests.post(url, json=data)
    else:
        logger.info(f'{fn_name}: No state change, will not trigger anything')
    
def handle_car_leave_lot(lot_number):
    fn_name = 'handle_car_leave_lot'
    # Check if lot is available (lot availability should be false)
    lot_availability = get_data_from_db(api_endpoint_constants.DB_GET_LOT_AVAILABILITY_ENDPOINT, lot_number)
    
    if lot_availability == False:
        update_lot_availability(lot_number, True, fn_name)
    else:
        logger.info(f'{fn_name}: No state change, will not trigger anything')

def handle_receive_ml_entrance_carplate(carplate):
    fn_name = 'handle_receive_ml_entrance_carplate'
    publish_to_topic(mqtt_topic_constants.STATUS_ENTRANCE_CARPLATE_TOPIC, carplate, fn_name)
    # Add car entry to db to indicate car entered carpark
    path = api_endpoint_constants.DB_ADD_ENTRY_ENDPOINT
    data = { 'carplate': carplate }
    post_data_to_db(path, data)
        
def handle_receive_ml_entrance_human_presence(human_presence):
    fn_name = 'handle_receive_ml_entrance_human_presence'
    publish_to_topic(mqtt_topic_constants.STATUS_ENTRANCE_HUMAN_PRESENCE_TOPIC, human_presence, fn_name)

def handle_receive_ml_exit_carplate(carplate):
    fn_name = 'handle_receive_ml_exit_carplate'
    publish_to_topic(mqtt_topic_constants.STATUS_EXIT_CARPLATE_TOPIC, carplate, fn_name)
    try:
        send_parking_fee_to_gantry(carplate)
    except Exception as e:
        logger.error(f'{fn_name}: {e}')
    
def send_parking_fee_to_gantry(carplate):
    fn_name = 'send_parking_fee_to_gantry'
    # Rounded up the hour, 1h = $2.5
    try:
        car_entrance_time = get_data_from_db(api_endpoint_constants.DB_GET_CAR_LAST_ENTRY_TIME_ENDPOINT, carplate)
        current_time = datetime.now(timezone.utc)
        time_difference = current_time - car_entrance_time
        parking_duration = math.ceil(time_difference.total_seconds() / 3600)
        parking_fee = parking_duration * 2.5
        logger.info(f'{fn_name}: Parking fee for {carplate} is ${parking_fee} for {parking_duration} hours')
        publish_to_topic(mqtt_topic_constants.STATUS_EXIT_PARKING_FEE_TOPIC, parking_fee, fn_name)
    except Exception as e:
        publish_to_topic(mqtt_topic_constants.STATUS_EXIT_PARKING_FEE_TOPIC, None, fn_name)
        raise Exception(f'Process parking fee error: {e}')

def handle_receive_ml_lot_carplate(topic, carplate):
    fn_name = 'handle_receive_ml_lot_carplate'
    lot_number = topic.split('/')[-1]
    logger.info(f'{fn_name}: lot_number: {lot_number}, carplate: {carplate}')
    # Update database to indicate car has parked at certain lot id
    path = api_endpoint_constants.DB_UPDATE_CAR_LOT_ENTRY_ENDPOINT
    data = {
        'carplate': carplate,
        'lotId': lot_number
    }
    put_data_to_db(path, data)

def on_connect(client, userdata, flags, rc):
    logger.info('Connected with result code: ' + str(rc))
    
    # Subscribe to cars coming to gantries (entrance, exit)
    client.subscribe(mqtt_topic_constants.EVENT_GANTRY_TOPIC + '#')
    # Subscribe to get carplate of cars coming into carpark
    client.subscribe(mqtt_topic_constants.STATUS_ML_ENTRANCE_CARPLATE_TOPIC)
    # Subscribe to get human presence at entrance
    client.subscribe(mqtt_topic_constants.STATUS_ML_ENTRANCE_HUMAN_PRESENCE_TOPIC)
    # Subscribe to get carplate of cars going out of carpark
    client.subscribe(mqtt_topic_constants.STATUS_ML_EXIT_CARPLATE_TOPIC)
    
    # Subcribe to cars parking/leaving at/from lots
    client.subscribe(mqtt_topic_constants.EVENT_LOT_TOPIC + '#')
    # Subscribe to get carplate of cars parking/leaving at/from lots
    client.subscribe(mqtt_topic_constants.STATUS_ML_LOT_CARPLATE_TOPIC + '#')
    
def on_message(client, userdata, message):
    topic = message.topic
    msg = message.payload.decode('utf-8')
    logger.info(f'Received message "{msg}" from topic "{topic}"')

    if topic.startswith(mqtt_topic_constants.EVENT_GANTRY_TOPIC):
        handle_gantry_event(topic, msg)
    elif topic.startswith(mqtt_topic_constants.EVENT_LOT_TOPIC):
        handle_lot_event(topic, msg)
    elif topic == mqtt_topic_constants.STATUS_ML_ENTRANCE_CARPLATE_TOPIC:
        handle_receive_ml_entrance_carplate(msg)
    elif topic == mqtt_topic_constants.STATUS_ML_ENTRANCE_HUMAN_PRESENCE_TOPIC:
        handle_receive_ml_entrance_human_presence(msg)
    elif topic == mqtt_topic_constants.STATUS_ML_EXIT_CARPLATE_TOPIC:
        handle_receive_ml_exit_carplate(msg)
    elif topic.startswith(mqtt_topic_constants.STATUS_ML_LOT_CARPLATE_TOPIC):
        handle_receive_ml_lot_carplate(topic, msg)
    else:
        logger.error(f'Received unknown topic: {topic}')
    
def get_data_from_db(path, param=None):
    url = f'http://{connection_constants.DB_IP}:{connection_constants.DB_PORT}{path}'
    if param:
        url += f'?data={param}'
    response = requests.get(url)
    if response.status_code == status_code_constants.SUCCESS:
        result = response.json()['result']
        logger.info(f'GET request to {url} was successful: {result}')
        return result
    else:
        error_msg = response.json()['error']
        logger.error(f'Cannot get data from {url}: {response.status_code}: {error_msg}')
        return None
    
def post_data_to_db(path, data):
    url = f'http://{connection_constants.DB_IP}:{connection_constants.DB_PORT}{path}'
    response = requests.post(url, json=data)

    if response.status_code == status_code_constants.SUCCESS:
        result = response.json()['result']
        logger.info(f'POST request to {url} was successful: {result}')
    else:
        error_msg = response.json()['error']
        logger.error(f'POST request to {url} failed: {response.status_code}: {error_msg}')
        
def put_data_to_db(path, data):
    url = f'http://{connection_constants.DB_IP}:{connection_constants.DB_PORT}{path}'
    response = requests.put(url, json=data)

    if response.status_code == status_code_constants.SUCCESS:
        result = response.json()['result']
        logger.info(f'PUT request to {url} was successful: {result}')
    else:
        error_msg = response.json()['error']
        logger.error(f'PUT request failed to {url}: {response.status_code}: {error_msg}')

if __name__ == '__main__':
    number_of_lots = get_data_from_db(api_endpoint_constants.DB_GET_NUMBER_OF_LOTS_ENDPOINT)
    if number_of_lots is None:
        logger.error(f'Cannot get total number of lots')
        exit(1)
        
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(connection_constants.BROKER_IP, connection_constants.BROKEN_PORT, 60)
    client.loop_forever()
