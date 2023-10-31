import requests
import json

# TODO: Replace if necessary
DATABASE_HOST = 'localhost'
DATABASE_PORT = 5000

def db_get_car_entrance_time(carplate):
    log_msg = 'Get car entrance time.'
    url = 'http://{}:{}/db/read-car-entrance-time?carplate={}'.format(DATABASE_HOST, DATABASE_PORT, carplate)
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        entrance_time = data.get('entranceTime')
        if entrance_time:
            print('[DB SUCCESS]: {}', log_msg)
            return entrance_time
        else:
            print('[DB FAILURE]: {} Status code: {}', log_msg, response.status_code)
    else:
        print('[DB FAILURE]: {} Status code: {}', log_msg, response.status_code)


def db_store_carplate(carplate):
    log_msg = 'Store carplate number.'
    url = 'http://{}:{}/db/create-car-enter'.format(DATABASE_HOST, DATABASE_PORT)
    headers = {'Content-Type': 'application/json'}
    body = {
        'carplate': carplate
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    # Check the response
    if response.status_code == 200:
        print('[DB SUCCESS]: {}', log_msg)
    else:
        print('[DB FAILURE]: {} Status code: {}', log_msg, response.status_code)

def db_get_nearest_lot():
    log_msg = 'Get nearest lot number.'
    url = 'http://{}:{}/db/get-nearest-lot'.format(DATABASE_HOST, DATABASE_PORT)
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        lot_number = data.get('lotNumber')
        if lot_number:
            print('[DB SUCCESS]: {}', log_msg)
            return lot_number
        else:
            print('[DB FAILURE]: {} Status code: {}', log_msg, response.status_code)
    else:
        print('[DB FAILURE]: {} Status code: {}', log_msg, response.status_code)

def db_store_carplate_and_lot_number(carplate_number, lot_number):
    log_msg = 'Store carplate and lot number.'
    url = 'http://{}:{}/db/create-car-park'.format(DATABASE_HOST, DATABASE_PORT)
    headers = {'Content-Type': 'application/json'}
    # TODO: Replace key if necessary, check with db
    body = {
        'lotNumber': lot_number,
        'carplateNumber': carplate_number
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    # Check the response
    if response.status_code == 200:
        print('[DB SUCCESS]: {}', log_msg)
    else:
        print('[DB FAILURE]: {} Status code: {}', log_msg, response.status_code)

def db_update_lot_availability(lot_number, is_available):
    log_msg = 'Update lot availability.'
    url = 'http://{}:{}/db/update-lot-availability'.format(DATABASE_HOST, DATABASE_PORT)
    headers = {'Content-Type': 'application/json'}
    # TODO: Replace key if necessary, check with db
    body = {
        'lotNumber': lot_number,
        'isAvailable': is_available
    }
    response = requests.put(url, headers=headers, data=json.dumps(body))
    # Check the response
    if response.status_code == 200:
        print('[DB SUCCESS]: {}', log_msg)
    else:
        print('[DB FAILURE]: {} Status code: {}', log_msg, response.status_code)
        