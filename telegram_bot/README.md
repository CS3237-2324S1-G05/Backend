# Smart Carpark Telgram Bot

This is a [Telegram bot](https://t.me/smart_carpark_bot) for drivers to check the locations (carpark lot number) of where their cars are parked at and the number of available lots at the carpark.

## Prerequisites

1. Install [Python 3.0](https://www.python.org/downloads/) (Preferably Python 3.10.12) on your machine.
2. Make sure the database on the cloud and API is running. Update **FLASK_BACKEND_IP** in `./constants.py` if necessary.

### Starting Telegram Bot

For initial setting up, please go through all the steps below.
For subsequent program execution, you may start from step 3.

1. Open your console. Create a Python virtual environment.

```
python3 -m venv venv
```

2. Activate the Python virtual environment.

```
source venv/bin/activate
```

3. Load the environment variables in `.env`.

```
source .env
```

4. Install packages.

```
pip install -r requirements.txt
```

5. Run the python bot script.

```
python3 bot.py
```

6. The bot should be running now. You can test it on Telegram with the commands below. [Here is the link to the Telegram bot](https://t.me/smart_carpark_bot).

## Commands for the Telegram Bot:

| Command syntax                         | Description                                                                                                                                                                                                      | Example              |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| /start                                 | Starts the bot.                                                                                                                                                                                                  | /start               |
| /where {car plate number with spacing} | Returns the location (carpark lot number) based on the car plate number given. Car plate number must follow the format specified [here](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Singapore). | /where SGD8888Z      |
| /available_lot_count                   | Returns the number of available lots in the carpark.                                                                                                                                                             | /available_lot_count |
