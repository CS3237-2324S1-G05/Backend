BROKER_IP = '192.168.43.156'
BROKEN_PORT = 1883

EVENT_GANTRY_TOPIC = 'event/gantry/'
EVENT_LOT_TOPIC = 'event/lot/'

# Request ESP32 to take image
CAM_CARPARK_TOPIC = 'cam/carpark'
CAM_LOT_TOPIC = 'cam/lot/'
CAM_GANTRY_ENTRANCE_TOPIC = 'cam/gantry/entrance'
CAM_GANTRY_EXIT_TOPIC = 'cam/gantry/exit'

# Receive data from ML
STATUS_ML_ENTRANCE_HUMAN_PRESENCE_TOPIC = 'status/ml/entrance/human-presence'
STATUS_ML_ENTRANCE_CARPLATE_TOPIC = 'status/ml/entrance/carplate'
STATUS_ML_EXIT_CARPLATE_TOPIC = 'status/ml/exit/carplate'
STATUS_ML_LOT_CARPLATE_TOPIC = 'status/ml/lot/carplate/'

# Send data to gantry
STATUS_ENTRANCE_HUMAN_PRESENCE_TOPIC = 'status/entrance/human-presence'
STATUS_ENTRANCE_NEAREST_LOT_TOPIC = 'status/entrance/nearest-lot'
STATUS_ENTRANCE_CARPLATE_TOPIC = 'status/entrance/carplate'
STATUS_ENTRANCE_NUMBER_OF_AVAILABLE_LOTS_TOPIC = 'status/entrance/number-of-available-lots'
STATUS_EXIT_PARKING_FEE_TOPIC = 'status/exit/parking-fee'
STATUS_EXIT_CARPLATE_TOPIC = 'status/exit/carplate'
