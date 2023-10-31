import paho.mqtt.client as mqtt
import datetime

from db_api_calls import db_store_carplate, db_get_nearest_lot, db_store_carplate_and_lot_number, db_update_lot_availability, db_get_car_entrance_time

BROKER_IP = '192.168.86.181'
BROKEN_PORT = 1883

# TODO: Number of lots?

EVENT_GANTRY_TOPIC = 'event/gantry/'
EVENT_LOT_TOPIC = 'event/lot/'

CAM_CARPARK_TOPIC = 'cam/carpark'
CAM_LOT_TOPIC = 'cam/lot/'
CAM_GANTRY_ENTRANCE_TOPIC = 'cam/gantry/entrance'
CAM_GANTRY_EXIT_TOPIC = 'cam/gantry/exit'

# STATUS_ENTRANCE_HUMAN_PRESENCE_TOPIC = 'status/entrance/human-presence'
STATUS_ENTRANCE_NEAREST_LOT_TOPIC = 'status/entrance/nearest-lot'
STATUS_ENTRANCE_CARPLATE_TOPIC = 'status/entrance/carplate'

STATUS_EXIT_CARPLATE_TOPIC = 'status/exit/carplate'
STATUS_EXIT_PARKING_FEE_TOPIC = 'status/exit/parking-fee'

STATUS_LOT_CARPLATE_TOPIC = 'status/lot/carplate/'

STATUS_ = 'ml/carplate/entrance'
STATUS_ = 'ml/carplate/exit'
STATUS_ = 'ml/human-presence'


# <0, 1, 2, 3>
NUMBER_OF_LOTS = 4

def publish_to_topic(topic, msg):
    print('Publish to {}'.format(topic))
    client.publish(topic, msg)

def handle_gantry_event(topic, msg):
    topic_levels = topic.split('/')
    gantry_name = topic_levels[-1]
    if gantry_name == 'entrance':
        # Inform ESP32 to take photo of carpark, gantry entrance
        publish_to_topic(CAM_CARPARK_TOPIC, 'DETECTED')
        publish_to_topic(CAM_GANTRY_ENTRANCE_TOPIC, 'DETECTED')
        
        # Return data to gantry
        # STATUS_ENTRANCE_HUMAN_PRESENCE_TOPIC: Done on flask
        # STATUS_ENTRANCE_CARPLATE_TOPIC: Done on another function in this file
        # nearest_lot = db_get_nearest_lot()
        # publish_to_topic(STATUS_ENTRANCE_NEAREST_LOT_TOPIC, nearest_lot)
    elif gantry_name == 'exit':
        # Inform ESP32 to take photo of gantry entrance
        publish_to_topic(STATUS_EXIT_CARPLATE_TOPIC, 'DETECTED')
        
        # STATUS_EXIT_PARKING_FEE_TOPIC: Done on another function in this file
    else:
        print('Unknown gantry name: {}'.format(gantry_name))
        
def handle_lot_event(topic, msg):
    topic_levels = topic.split('/')
    event_type = topic_levels[-2]  # Get the event type (park or leave)
    try:
        lot_number = int(topic_levels[-1])
    except ValueError:
        print('Invalid lot number: {}'.format(topic_levels[-1]))
        return
    if lot_number >= NUMBER_OF_LOTS:
        print('Unknown lot number: {}'.format(lot_number))
    
    if event_type == 'park':
        # Request ESP32 to take photo of lot/car plate
        publish_to_topic(CAM_LOT_TOPIC + str(lot_number), 'DETECTED')
    elif event_type == 'leave':
        # Update lot availability in DB
        db_update_lot_availability(lot_number, True)
    else:
        print('Unknown event type: {}'.format(event_type))

def on_connect(client, userdata, flags, rc):
    print('Connected with result code: ' + str(rc))
    
    # Subscribe to cars coming to gantries (entrance, exit)
    client.subscribe(EVENT_GANTRY_TOPIC + '#')
    # Subscribe to get carplate of cars coming into carpark
    client.subscribe(STATUS_ENTRANCE_CARPLATE_TOPIC)
    # Subscribe to get carplate of cars going out of carpark
    client.subscribe(STATUS_EXIT_CARPLATE_TOPIC)
    
    # Subcribe to cars parking at lots
    client.subscribe(EVENT_LOT_TOPIC + '#')

def on_message(client, userdata, message):
    topic = message.topic
    msg = message.payload.decode('utf-8')
    print('Received message "{}" from topic "{}"'.format(msg, topic))
  
    if topic.startswith(EVENT_GANTRY_TOPIC):
        handle_gantry_event(topic, msg)
    elif topic.startswith(EVENT_LOT_TOPIC):
        handle_lot_event(topic, msg)
    elif topic == STATUS_ENTRANCE_CARPLATE_TOPIC:
        db_store_carplate(msg)
    elif topic == STATUS_EXIT_CARPLATE_TOPIC:
        car_entrance_time = db_get_car_entrance_time(msg)
        current_time = datetime.datetime.now()
        time_difference = current_time - car_entrance_time
        # Round up seconds to 1 minute, 50c per minute
        parking_fee = (time_difference.hour * 60 + time_difference.minute + 1) * 0.5
        publish_to_topic(STATUS_EXIT_PARKING_FEE_TOPIC, parking_fee)
    elif topic.startswith(STATUS_LOT_CARPLATE_TOPIC):
        lot_number = topic.split('/')[-1]
        db_store_carplate_and_lot_number(msg, lot_number)
    else:
        print('Unknown topic: {}'.format(topic))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_IP, BROKEN_PORT, 60)
client.loop_forever()
