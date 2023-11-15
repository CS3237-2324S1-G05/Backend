"""
Written by Venus Lim
CS3237 AY23/24 Semester 1 Group 5: Smart Carpark System
This is a MQTT pubsub client that publishes and subscribes to topics on the MQTT broker
and serves as a centralised backend for this system.
"""

import math
import paho.mqtt.client as mqtt
import requests
import time
from datetime import datetime

import sys
sys.path.append('../common_utils')
from logger import logger
import api_endpoint_constants
import mqtt_topic_constants
import connection_constants
import status_code_constants

def get_string_msg(msg):
  if not isinstance(msg, str):
    msg = str(msg)
  return msg

def publish_to_topic(topic, msg, fn_name):
  msg = get_string_msg(msg)
  logger.info(f'{fn_name}: Publish to {topic}, message: {msg}')
  client.publish(topic, msg)
  
def publish_to_topic_retain(topic, msg, fn_name):
  msg = get_string_msg(msg)
  logger.info(f'{fn_name}: Publish to {topic}, message: {msg}')
  client.publish(topic, msg, retain = True)

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
    
def inform_esp32_entrance():
  # Inform ESP32 to take photo of carpark, gantry entrance
  fn_name = 'inform_esp32_entrance'
  publish_to_topic(mqtt_topic_constants.CAM_CARPARK_TOPIC, '1', fn_name)
  time.sleep(6)
  publish_to_topic(mqtt_topic_constants.CAM_GANTRY_ENTRANCE_TOPIC, '1', fn_name)

def handle_car_at_entrance():
  fn_name = 'handle_car_at_entrance'
  inform_esp32_entrance()
  # Inform gantry the nearest lot (Return str(id) or str(None))
  nearest_available_lot = get_data_from_db(api_endpoint_constants.DB_GET_NEAREST_AVAILABLE_LOT_ENDPOINT)
  publish_to_topic(mqtt_topic_constants.STATUS_ENTRANCE_NEAREST_LOT_TOPIC, nearest_available_lot, fn_name)

def inform_esp32_exit():
  # Inform ESP32 to take photo of gantry entrance
  fn_name = 'inform_esp32_exit'
  time.sleep(2)
  publish_to_topic(mqtt_topic_constants.CAM_GANTRY_EXIT_TOPIC, '1', fn_name)
  
def handle_car_at_exit():
  inform_esp32_exit()
      
def handle_lot_event(topic, msg):
  fn_name = 'handle_lot_event'
  topic_levels = topic.split('/')
  event_type = topic_levels[-2]  # Get the event type (park or leave)
  try:
    lot_number = int(topic_levels[-1])
  except ValueError:
    logger.error(f'{fn_name}: Invalid lot number: {topic_levels[-1]}')
  if lot_number >= number_of_lots:
    logger.error(f'{fn_name}: Lot number does not exist: {lot_number}')
  
  try:
    if event_type == 'park':
      handle_car_park_lot(lot_number)
    elif event_type == 'leave':
      handle_car_leave_lot(lot_number)
    else:
      logger.error(f'{fn_name}: Unknown event type: {event_type}')
  except Exception as e:
    logger.error(f'{fn_name}: {e}')
      
def send_number_of_available_lots():
  fn_name = 'send_number_of_available_lots'
  number_of_available_lots = get_data_from_db(api_endpoint_constants.DB_GET_NUMBER_OF_AVAILABLE_LOTS_ENDPOINT)
  publish_to_topic_retain(mqtt_topic_constants.STATUS_NUMBER_OF_AVAILABLE_LOTS_TOPIC, number_of_available_lots, fn_name)
      
def update_lot_availability(lot_number, is_available):
  path = api_endpoint_constants.DB_UPDATE_LOT_AVAILABILITY_ENDPOINT
  data = {
    'lotId': lot_number,
    'isAvailable': is_available
  }
  post_data_to_db(path, data)
  send_number_of_available_lots()

def inform_esp32_lot(lot_number):
  fn_name = 'inform_esp32_lot'
  # Request ESP32 to take photo of lot/carplate
  publish_to_topic(mqtt_topic_constants.CAM_LOT_TOPIC + str(lot_number), '1', fn_name)

def handle_car_park_lot(lot_number):
  fn_name = 'handle_car_park_lot'
  # Check if lot is available (lot availability should be true)  
  lot_availability = get_data_from_db(api_endpoint_constants.DB_GET_LOT_AVAILABILITY_ENDPOINT, lot_number)
  
  if lot_availability == True:      
    inform_esp32_lot(lot_number)
  else:
    logger.info(f'{fn_name}: No state change, will not trigger anything')
  
def handle_car_leave_lot(lot_number):
  fn_name = 'handle_car_leave_lot'
  # Check if lot is available (lot availability should be false)
  lot_availability = get_data_from_db(api_endpoint_constants.DB_GET_LOT_AVAILABILITY_ENDPOINT, lot_number)
  
  if lot_availability == False:
    update_lot_availability(lot_number, True)
  else:
    logger.info(f'{fn_name}: No state change, will not trigger anything')

def handle_receive_ml_entrance_carplate(carplate):
  fn_name = 'handle_receive_ml_entrance_carplate'
  if carplate == '':
    # No flow if carplate number cannot be detected
    logger.error(f'{fn_name}: Carplate is empty')
  elif carplate == 'INVALID':
    logger.error(f'{fn_name}: Carplate is invalid')
  else:
    logger.info(f'{fn_name}: Carplate: {carplate}')
    # Add car entry to db to indicate car entered carpark if car hasnt enter
    path = api_endpoint_constants.DB_ADD_ENTRY_ENDPOINT
    data = { 'carplate': carplate }
    if post_data_to_db(path, data) is None:
      logger.error(f'{fn_name}: Cannot add car entry to db since car has already entered carpark')
    else:
      logger.info(f'{fn_name}: Added car entry to db')
      publish_to_topic(mqtt_topic_constants.STATUS_ENTRANCE_CARPLATE_TOPIC, carplate, fn_name)    
      
def handle_receive_ml_entrance_human_presence(human_presence):
  fn_name = 'handle_receive_ml_entrance_human_presence'
  publish_to_topic(mqtt_topic_constants.STATUS_ENTRANCE_HUMAN_PRESENCE_TOPIC, human_presence, fn_name)

def handle_receive_ml_exit_carplate(carplate):
  fn_name = 'handle_receive_ml_exit_carplate'
  if carplate == '':
    # No flow if carplate number cannot be detected
    logger.error(f'{fn_name}: Carplate is empty')
  elif carplate == 'INVALID':
    logger.error(f'{fn_name}: Carplate is invalid')
  else:
    logger.info(f'{fn_name}: Carplate: {carplate}')
    publish_to_topic(mqtt_topic_constants.STATUS_EXIT_CARPLATE_TOPIC, carplate, fn_name)
    try:
      process_parking_fee(carplate)
    except Exception as e:
      logger.error(f'{fn_name}: {e}')
      
def process_parking_fee(carplate):
  fn_name = 'send_parking_fee_to_gantry'
  try:
    car_entrance_time = get_data_from_db(api_endpoint_constants.DB_GET_CAR_LAST_ENTRY_TIME_ENDPOINT, carplate)
    if car_entrance_time is None:
      logger.error(f'{fn_name}: Cannot get car {carplate} last entry time')
    else:
      data = get_data_from_db(api_endpoint_constants.DB_GET_CAR_LAST_EXIT_TIME_ENDPOINT, carplate)   
      if data is None:
        logger.info(f'{fn_name}: Car {carplate} has not exited carpark')
        
        car_entrance_time = datetime.strptime(car_entrance_time, "%a, %d %b %Y %H:%M:%S %Z")
        current_time = datetime.utcnow()  
        current_time_str = current_time.isoformat()
        logger.info(f'{fn_name}: Current time (exit time): {current_time}, Car entrance time: {car_entrance_time}')              
        time_difference = (current_time - car_entrance_time).total_seconds()
        
        # Free for first 2 minutes
        parking_fee = 0
        if time_difference > 120:
          # Charge if exceed 2 minutes, Rounded up the hour, 1h = $2.5
          parking_duration = math.ceil(time_difference / 3600)
          parking_fee = "{:.2f}".format(round(parking_duration * 2.5, 2))
          logger.info(f'{fn_name}: Parking fee for {carplate} is ${parking_fee} for {parking_duration} hours')
        
        put_data_to_db(api_endpoint_constants.DB_UPDATE_CAR_EXIT_ENTRY_ENDPOINT, 
                            { 'carplate': carplate, 'exitTime': current_time_str, 'duration': time_difference, 'fee': parking_fee })
        publish_to_topic(mqtt_topic_constants.STATUS_EXIT_PARKING_FEE_TOPIC, parking_fee, fn_name)
      else:
        logger.error(f'Car {carplate} has already exited carpark')
        publish_to_topic(mqtt_topic_constants.STATUS_EXIT_PARKING_FEE_TOPIC, None, fn_name)
  except Exception as e:
    publish_to_topic(mqtt_topic_constants.STATUS_EXIT_PARKING_FEE_TOPIC, None, fn_name)
    raise Exception(f'Process parking fee error: {e}')

def handle_receive_ml_lot_carplate(topic, carplate):
  fn_name = 'handle_receive_ml_lot_carplate'
  lot_number = topic.split('/')[-1]
  if carplate == '':
    # No flow if carplate number cannot be detected
    logger.error(f'{fn_name}: Carplate is empty, but detected something at lot {lot_number}')
  elif carplate == 'INVALID':
    logger.error(f'{fn_name}: Carplate is invalid')
  else:
    logger.info(f'{fn_name}: Carplate: {carplate} at lot {lot_number}')
    update_lot_availability(lot_number, False)
    
    # Update database to indicate car has parked at certain lot id
    path = api_endpoint_constants.DB_UPDATE_CAR_LOT_ENTRY_ENDPOINT
    data = {
      'carplate': carplate,
      'lotId': lot_number
    }
    put_data_to_db(path, data)
  
def get_data_from_db(path, param=None):
  url = f'http://{connection_constants.DB_IP}:{connection_constants.DB_PORT}{path}'
  if param is not None:
    url += f'?data={param}'
  logger.info(f'GET request to {url}')
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
  logger.info(f'POST request to {url}, data: {data}')
  response = requests.post(url, json=data)

  if response.status_code == status_code_constants.SUCCESS:
    message = response.json()['result']
    logger.info(f'POST request to {url} was successful: {message}')
    return message
  else:
    error_msg = response.json()['error']
    logger.error(f'POST request to {url} failed: {response.status_code}: {error_msg}')
    return None
      
def put_data_to_db(path, data):
  url = f'http://{connection_constants.DB_IP}:{connection_constants.DB_PORT}{path}'
  logger.info(f'PUT request to {url}, data: {data}')
  response = requests.put(url, json=data)

  if response.status_code == status_code_constants.SUCCESS:
    result = response.json()['result']
    logger.info(f'PUT request to {url} was successful: {result}')
  else:
    error_msg = response.json()['error']
    logger.error(f'PUT request failed to {url}: {response.status_code}: {error_msg}')

def on_connect(client, userdata, flags, rc):
  logger.info('Connected with result code: ' + str(rc))
  
  send_number_of_available_lots()
  
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
    
if __name__ == '__main__':
  number_of_lots = get_data_from_db(api_endpoint_constants.DB_GET_NUMBER_OF_LOTS_ENDPOINT)
  if number_of_lots is None:
    logger.error(f'Cannot get total number of lots')
    exit(1)
      
  client = mqtt.Client()
  client.on_connect = on_connect
  client.on_message = on_message

  client.connect(connection_constants.BROKER_IP, connection_constants.BROKER_PORT, 60)
  client.loop_forever()
