from flask import Flask, request, jsonify
import os
from datetime import timezone
from mongodb_class import Database

import sys
sys.path.append('../common_utils')
from logger import logger
import status_code_constants
import api_endpoint_constants

app = Flask(__name__)

# Returns carplate's latest lot id - str(int) or str(None) (str)
@app.route(api_endpoint_constants.DB_GET_CAR_LOT_ENDPOINT, methods=['GET'])
def handle_get_car_lot():
    carplate = request.args.get('data')
    if carplate:
        lot = db.get_car_lot(carplate)
        if lot:
            return jsonify({'result': lot}), status_code_constants.SUCCESS
        else:
            return jsonify({'error': f'Cannot find car {carplate} lot'}), status_code_constants.NOT_FOUND
    else:
        return jsonify({'error': 'Missing data (carplate) in the query string of the URL'}), status_code_constants.BAD_REQUEST

# Returns lotId or None (int)
@app.route(api_endpoint_constants.DB_GET_NEAREST_AVAILABLE_LOT_ENDPOINT, methods=['GET'])
def handle_get_nearest_available_lot():
    nearest_available_lot = db.get_nearest_available_lot()
    if nearest_available_lot:
        return jsonify({'result': str(nearest_available_lot)}), status_code_constants.SUCCESS
    else:
        return jsonify({'error': f'No available lots'}), status_code_constants.NOT_FOUND
        
# Returns count of available lots (int)
@app.route(api_endpoint_constants.DB_GET_NUMBER_OF_AVAILABLE_LOTS_ENDPOINT, methods=['GET'])
def handle_get_number_of_available_lots():
    number_of_available_lots = db.get_number_of_available_lots()
    return jsonify({'result': number_of_available_lots}), status_code_constants.SUCCESS

# Returns count of total lots (int)
@app.route(api_endpoint_constants.DB_GET_NUMBER_OF_LOTS_ENDPOINT, methods=['GET'])
def handle_get_number_of_lots():
    number_of_lots = db.get_number_of_lots()
    return jsonify({'result': number_of_lots}), status_code_constants.SUCCESS

# Returns True/False for lot availability (bool)
@app.route(api_endpoint_constants.DB_GET_LOT_AVAILABILITY_ENDPOINT, methods=['GET'])
def handle_get_lot_availability():
    lot_id = request.args.get('data')
    if lot_id:
        try:    
            lot_id = int(lot_id)
        except:
            return jsonify({'error': 'lotId must be an integer'}), status_code_constants.BAD_REQUEST
        try:
            lot_availability = db.get_availability(lot_id)
            return jsonify({'result': lot_availability}), status_code_constants.SUCCESS
        except Exception as e:
            logger.error(f'Cannot get availability: {e}')
            return jsonify({'error': f'{e}'}), status_code_constants.NOT_FOUND
    else:
        return jsonify({'error': 'Missing data (lot id) in the query string of the url'}), status_code_constants.BAD_REQUEST

# Returns time of last entry (str)
@app.route(api_endpoint_constants.DB_GET_CAR_LAST_ENTRY_TIME_ENDPOINT, methods=['GET'])
def handle_get_car_last_entry_time():
    carplate = request.args.get('data')
    if carplate:
        try:
            car_entrance_time = db.get_last_entry_time(carplate)
            return jsonify({'result': car_entrance_time.replace(tzinfo=timezone.utc)}), status_code_constants.SUCCESS
        except Exception as e:
            logger.error(f'Cannot get car last entry time: {e}')
            return jsonify({'error': f'{e}'}), status_code_constants.NOT_FOUND
    else:
        return jsonify({'error': 'Missing data (carplate) in the query string of the url'}), status_code_constants.BAD_REQUEST

# Returns whether lot availability is updated properly using message
@app.route(api_endpoint_constants.DB_UPDATE_LOT_AVAILABILITY_ENDPOINT, methods=['POST'])
def handle_update_lot_availability():
    data = request.get_json()
    if 'lotId' in data and 'isAvailable' in data:
        lot_id = data['lotId']
        try:
            lot_id = int(lot_id)
        except:
            return jsonify({'error': 'lotId must be an integer'}), status_code_constants.BAD_REQUEST
        try:
            is_available = bool(data['isAvailable'])
        except:
            return jsonify({'error': 'isAvailable must be a boolean'}), status_code_constants.BAD_REQUEST
        try:
            db.update_lot_availability(lot_id, is_available)
            return jsonify({'result': f'Lot {lot_id} availability updated to {is_available} successfully'}), status_code_constants.SUCCESS
        except Exception as e:
            logger.error(f'Cannot update lot availability: {e}')
            return jsonify({'error': f'{e}'}), status_code_constants.INTERNAL_SERVER_ERROR
    else:
        return jsonify({'error': 'Missing lotId or isAvailable in the request body'}), status_code_constants.BAD_REQUEST

@app.route(api_endpoint_constants.DB_UPDATE_CAR_LOT_ENTRY_ENDPOINT, methods=['PUT'])
def handle_update_car_lot_entry():
    data = request.get_json()
    if 'carplate' in data and 'lotId' in data:
        carplate = data['carplate']
        lot_id = data['lotId']
        try:
            db.update_car_lot_entry(carplate, lot_id)
            return jsonify({'message': f'Car {carplate} lot entry updated to lot {lot_id} successfully'}), status_code_constants.SUCCESS
        except Exception as e:
            logger.error(f'Cannot update car lot entry: {e}')
            return jsonify({'error': f'{e}'}), status_code_constants.INTERNAL_SERVER_ERROR
    else:
        return jsonify({'error': 'Missing carplate or lotId in the request body'}), status_code_constants.BAD_REQUEST

@app.route(api_endpoint_constants.DB_ADD_ENTRY_ENDPOINT, methods=['POST'])
def handle_add_entry():
    data = request.get_json()
    if 'carplate' in data:
        carplate = data['carplate']
        try:
            db.add_entry(carplate)
            return jsonify({'message': f'Entry for car {carplate} added successfully'}), status_code_constants.SUCCESS
        except Exception as e:
            return jsonify(f'Has issues adding entry for car {carplate}: {e}'), status_code_constants.INTERNAL_SERVER_ERROR
    else:
        return jsonify({'error': 'Missing carplate in the request body'}), status_code_constants.BAD_REQUEST

if __name__ == '__main__':
    db_username = os.getenv('DB_USERNAME')
    db_password = os.getenv('DB_PASSWORD')
    try:
        db = Database(logger, db_username, db_password)
        logger.info(f"Connected to database")
    except Exception as e:
        logger.error(f'Cannot connect to database: {e}')
        exit(1)
    app.run(host='0.0.0.0', port= 6000)
    