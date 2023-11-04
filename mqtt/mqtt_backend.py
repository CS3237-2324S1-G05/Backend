import paho.mqtt.client as mqtt
import datetime
import os
import math

from mongodb_class import Database
import constants

# Please read:
# Remove stub, its to trigger the ML model to run since theres no communication with ESP32 now

import requests

# TODO:
# Test thoroughly
# Log more (perhaps with timing)
# DB can contain more data (this can be used for dashboard if we are making)

def publish_to_topic(topic, msg):
    print(f'Publish to {topic}')
    client.publish(topic, msg)

def handle_gantry_event(topic, msg):
    topic_levels = topic.split('/')
    gantry_name = topic_levels[-1]
    if gantry_name == 'entrance':
        handle_car_at_entrance()
    elif gantry_name == 'exit':
        handle_car_at_exit()
    else:
        print(f'Unknown gantry name: {gantry_name}')

def handle_car_at_entrance():
    # Inform ESP32 to take photo of carpark, gantry entrance
    publish_to_topic(constants.CAM_CARPARK_TOPIC, 'DETECTED')
    publish_to_topic(constants.CAM_GANTRY_ENTRANCE_TOPIC, 'DETECTED')
    
    # Stub
    response = requests.post('http://{}:{}/{}'.format('localhost', 7000, 'backend/human-recognition'))
    # Stub
    response = requests.post('http://{}:{}/{}'.format('localhost', 7000, 'backend/carplate-recognition/entrance'))
    
    # Inform gantry the nearest lot (Return str(id) or str(None))
    nearest_available_lot = str(db.get_nearest_available_lot())
    publish_to_topic(constants.STATUS_ENTRANCE_NEAREST_LOT_TOPIC, nearest_available_lot)
    
    # Inform gantry number of available lots (return str(count))
    number_of_available_lots = str(db.get_number_of_available_lots())
    publish_to_topic(constants.STATUS_ENTRANCE_NUMBER_OF_AVAILABLE_LOTS_TOPIC, number_of_available_lots)
    
def handle_car_at_exit():
    # Inform ESP32 to take photo of gantry entrance
    publish_to_topic(constants.CAM_GANTRY_EXIT_TOPIC, 'DETECTED')
    
    response = requests.post('http://{}:{}/{}'.format('localhost', 7000, 'backend/carplate-recognition/exit'))
        
def handle_lot_event(topic, msg):
    topic_levels = topic.split('/')
    event_type = topic_levels[-2]  # Get the event type (park or leave)
    try:
        lot_number = int(topic_levels[-1])
    except ValueError:
        print(f'Invalid lot number: {topic_levels[-1]}')
        return
    if lot_number >= number_of_lots:
        print(f'Unknown lot number: {lot_number}')
    
    if event_type == 'park':
        handle_car_park_lot(lot_number)
    elif event_type == 'leave':
        handle_car_leave_lot(lot_number)
    else:
        print(f'Unknown event type: {event_type}')

def handle_car_park_lot(lot_number):
    # Update lot availability in DB
    try:
        db.update_availability(lot_number, False)
    except Exception as e:
        print(f'Error: {e}')
        
    # Request ESP32 to take photo of lot/car plate
    publish_to_topic(constants.CAM_LOT_TOPIC + str(lot_number), 'DETECTED')
    
    response = requests.post('http://{}:{}/{}'.format('localhost', 7000, 'backend/carplate-recognition/lot'))

def handle_car_leave_lot(lot_number):
    # Update lot availability in DB
    try:
        db.update_availability(lot_number, True)
    except Exception as e:
        print(f'Error: {e}')

def handle_receive_ml_entrance_carplate(carplate):
    publish_to_topic(constants.STATUS_ENTRANCE_CARPLATE_TOPIC, carplate)
    # Add car entry to db to indicate car entered carpark
    try:
        db.add_entry(carplate)
    except Exception as e:
        print(f'Error: {e}')
        
def handle_receive_ml_entrance_human_presence(human_presence):
    publish_to_topic(constants.STATUS_ENTRANCE_HUMAN_PRESENCE_TOPIC, human_presence)

def handle_receive_ml_exit_carplate(carplate):
    publish_to_topic(constants.STATUS_EXIT_CARPLATE_TOPIC, carplate)
    send_parking_fee_to_gantry(carplate)
    
def send_parking_fee_to_gantry(carplate):
    # Get car entrance time from db
    try:
        car_entrance_time = db.get_last_entry_time(carplate)
        current_time = datetime.datetime.now()
        time_difference = current_time - car_entrance_time
        parking_duration = math.ceil(time_difference.total_seconds() / 3600)
        parking_fee = parking_duration * 2.5
        print(f'Parking fee for {carplate} is ${parking_fee} for {parking_duration} hours')
        publish_to_topic(constants.STATUS_EXIT_PARKING_FEE_TOPIC, parking_fee)
    except Exception as e:
        print(f'Error: {e}')
        publish_to_topic(constants.STATUS_EXIT_PARKING_FEE_TOPIC, None)

def handle_receive_ml_lot_carplate(topic, carplate):
    lot_number = topic.split('/')[-1]
    print(f'lot_number: {lot_number}, carplate: {carplate}')
    # Update database to indicate car has parked at certain lot id
    try:
        db.update_car_lot_entry(carplate, lot_number)
    except Exception as e:
        print(f'Error: {e}')

def on_connect(client, userdata, flags, rc):
    print('Connected with result code: ' + str(rc))
    
    # Subscribe to cars coming to gantries (entrance, exit)
    client.subscribe(constants.EVENT_GANTRY_TOPIC + '#')
    # Subscribe to get carplate of cars coming into carpark
    client.subscribe(constants.STATUS_ML_ENTRANCE_CARPLATE_TOPIC)
    # Subscribe to get human presence at entrance
    client.subscribe(constants.STATUS_ML_ENTRANCE_HUMAN_PRESENCE_TOPIC)
    # Subscribe to get carplate of cars going out of carpark
    client.subscribe(constants.STATUS_ML_EXIT_CARPLATE_TOPIC)
    
    # Subcribe to cars parking/leaving at/from lots
    client.subscribe(constants.EVENT_LOT_TOPIC + '#')
    # Subscribe to get carplate of cars parking/leaving at/from lots
    client.subscribe(constants.STATUS_ML_LOT_CARPLATE_TOPIC + '#')
    
def on_message(client, userdata, message):
    topic = message.topic
    msg = message.payload.decode('utf-8')
    print(f'Received message "{msg}" from topic "{topic}"')
  
    if topic.startswith(constants.EVENT_GANTRY_TOPIC):
        handle_gantry_event(topic, msg)
    elif topic.startswith(constants.EVENT_LOT_TOPIC):
        handle_lot_event(topic, msg)
    elif topic == constants.STATUS_ML_ENTRANCE_CARPLATE_TOPIC:
        handle_receive_ml_entrance_carplate(msg)
    elif topic == constants.STATUS_ML_ENTRANCE_HUMAN_PRESENCE_TOPIC:
        handle_receive_ml_entrance_human_presence(msg)
    elif topic == constants.STATUS_ML_EXIT_CARPLATE_TOPIC:
        handle_receive_ml_exit_carplate(msg)
    elif topic.startswith(constants.STATUS_ML_LOT_CARPLATE_TOPIC):
        handle_receive_ml_lot_carplate(topic, msg)
    else:
        print(f'Unknown topic: {topic}')

if __name__ == '__main__':
    db_username = os.getenv('DB_USERNAME')
    db_password = os.getenv('DB_PASSWORD')
    db = Database(db_username, db_password)
    
    number_of_lots = db.get_number_of_lots()
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(constants.BROKER_IP, constants.BROKEN_PORT, 60)
    client.loop_forever()
