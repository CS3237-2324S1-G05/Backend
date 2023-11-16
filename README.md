# Backend, Database, Bot for Smart Carpark

This repository consists of codes for

1. Backend (running MQTT Client and Flask API endpoints)
2. Database (communicated through Flask API)
3. Telegram Bot (requires Flask for database to be running)

The actual database is running on MongoDB Atlas.

## Port numbers

- [Backend] MQTT Broker: 1883
- [Backend] Flask Endpoints: 3237
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
- /db-backend/get-car-last-exit-time

## Database Flask Endpoints

- /backend/human-recognition
- /backend/carplate-recognition/entrance
- /backend/carplate-recognition/exit
- /backend/carplate-recognition/lot
