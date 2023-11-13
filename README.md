# Backend and Database for Smart Carpark

This repository consists of codes for the backend (running MQTT Client and Flask API endpoints) and database (communicated through Flask API).

The actual database is running on MongoDB Atlas.

## Port numbers

- [Backend] MQTT Broker: 1883
- [Backend] Flask Endpoints: 7000
- [Database] Flask Endpoints: 6000

## Backend Flask Endpoints

- /db-backend/get-car-lot
- /db-backend/get-nearest-available-lot
- /db-backend/get-number-of-available-lots
- /db-backend/get-number-of-lots
- /db-backend/get-lot-availability
- /db-backend/get-car-last-entry-time
- /db-backend/update-lot-availability
- /db-backend/update-lot-carplate
- /db-backend/update-car-lot-entry
- /db-backend/add-entry
- /db-backend/update-car-exit-entry

## Database Flask Endpoints

- /backend/human-recognition
- /backend/carplate-recognition/entrance
- /backend/carplate-recognition/exit
- /backend/carplate-recognition/lot
