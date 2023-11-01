import paho.mqtt.client as mqtt
import datetime

from mongodb_class import Database

BROKER_IP = 'localhost'
BROKEN_PORT = 1883

EVENT_GANTRY_TOPIC = 'event/gantry/'
EVENT_LOT_TOPIC = 'event/lot/'

# Request ESP32 to take image
CAM_CARPARK_TOPIC = 'cam/carpark'
CAM_LOT_TOPIC = 'cam/lot/'
CAM_GANTRY_ENTRANCE_TOPIC = 'cam/gantry/entrance'
CAM_GANTRY_EXIT_TOPIC = 'cam/gantry/exit'

# Get carplate numbers from ML
STATUS_ENTRANCE_CARPLATE_TOPIC = 'status/entrance/carplate'
STATUS_EXIT_CARPLATE_TOPIC = 'status/exit/carplate'
STATUS_LOT_CARPLATE_TOPIC = 'status/lot/carplate/'

# Send number of lots to gantry
STATUS_NUMBER_OF_LOTS_TOPIC = 'status/entrance/number-of-available-lots'
# Send nearest lot number to gantry when car enters
STATUS_ENTRANCE_NEAREST_LOT_TOPIC = 'status/entrance/nearest-lot'
# Send parking fee of car to gantry when car exits
STATUS_EXIT_PARKING_FEE_TOPIC = 'status/exit/parking-fee'

# TODO: db: Get value from db instead
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
        # Inform gantry the nearest lot
        # TODO: db
        nearest_lot = db.get_nearest_lot()
        publish_to_topic(STATUS_ENTRANCE_NEAREST_LOT_TOPIC, nearest_lot)
    elif gantry_name == 'exit':
        # Inform ESP32 to take photo of gantry entrance
        publish_to_topic(CAM_GANTRY_EXIT_TOPIC, 'DETECTED')
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
        # TODO: db: Update lot availability in DB
        db.update_availability(lot_number, True)
    else:
        print('Unknown event type: {}'.format(event_type))
        
def send_parking_fee_to_gantry(carplate):
    # TODO: db
    car_entrance_time = db.get_last_entry(carplate)
    current_time = datetime.datetime.now()
    time_difference = current_time - car_entrance_time
    parking_duration = time_difference.hour
    if time_difference.minute > 0 or time_difference.second > 0:
        parking_duration += 1
    parking_fee = parking_duration * 2.5
    publish_to_topic(STATUS_EXIT_PARKING_FEE_TOPIC, parking_fee)

def on_connect(client, userdata, flags, rc):
    print('Connected with result code: ' + str(rc))
    
    # Subscribe to cars coming to gantries (entrance, exit)
    client.subscribe(EVENT_GANTRY_TOPIC + '#')
    # Subscribe to get carplate of cars coming into carpark
    client.subscribe(STATUS_ENTRANCE_CARPLATE_TOPIC)
    # Subscribe to get carplate of cars going out of carpark
    client.subscribe(STATUS_EXIT_CARPLATE_TOPIC)
    
    # Subcribe to cars parking/leaving at/from lots
    client.subscribe(EVENT_LOT_TOPIC + '#')
    # Subscribe to get carplate of cars parking/leaving at/from lots
    client.subscribe(STATUS_LOT_CARPLATE_TOPIC + '#')
    


def on_message(client, userdata, message):
    topic = message.topic
    msg = message.payload.decode('utf-8')
    print('Received message "{}" from topic "{}"'.format(msg, topic))
  
    if topic.startswith(EVENT_GANTRY_TOPIC):
        handle_gantry_event(topic, msg)
    elif topic.startswith(EVENT_LOT_TOPIC):
        handle_lot_event(topic, msg)
    elif topic == STATUS_ENTRANCE_CARPLATE_TOPIC:
        # TODO: db
        db.add_entry(msg)
    elif topic == STATUS_EXIT_CARPLATE_TOPIC:
        send_parking_fee_to_gantry(msg)
    elif topic.startswith(STATUS_LOT_CARPLATE_TOPIC):
        lot_number = topic.split('/')[-1]
        print('lot_number: {}, carplate: {}'.format(lot_number, msg))
        # TODO: db: edit db.add_entry to update lot number
        db.add_entry(msg, lot_number)
    else:
        print('Unknown topic: {}'.format(topic))
        
db = Database()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_IP, BROKEN_PORT, 60)
client.loop_forever()
