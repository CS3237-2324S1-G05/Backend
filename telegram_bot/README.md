# Smart Carpark Telegram Bot Codebase 🚗💡

Welcome to the GitHub repository for the Smart Carpark system's Telegram Bot! This is a [Telegram bot](https://t.me/smart_carpark_bot) for drivers check the

1. Locations (carpark lot number) of where their cars are parked at
2. Number of available lots at the carpark
3. Parking fee for their cars at the point they send the command

This is done as part of the Project for CS3237 - Introduction to Internet of Things, AY23/24 Semester 1.

Done by Group 5!

## Repository Structure 🗂️

Here's a guide to what you'll find in this repository:

- `.env`: Consists of Telegram bot secret key

- `bot.py`: Main python script for the bot

- `constants.py`: Constants file for `bot.py`

- `requirements.txt`: Consists of required packages for `bot.py`

## Setup & Installation ⚙️

1. Install [Python 3.0](https://www.python.org/downloads/) (Preferably Python 3.10.12) on your machine.
2. Make sure the database on MongoDB and Flask for the database are running. Update **FLASK_BACKEND_IP** in `./constants.py` if this program and the Flask for the database are running on different machines.

### Initial Setting and Starting Up of Telegram Bot

This steps written for Ubuntu and Mac OS.

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

## Subsequent Starting Up of Telegram Bot

This steps written for Ubuntu and Mac OS.

1. Open your console. Activate the Python virtual environment.

```
source venv/bin/activate
```

2. Load the environment variables in `.env`.

```
source .env
```

3. Run the python bot script.

```
python3 bot.py
```

4. The bot should be running now. You can test it on Telegram with the commands below. [Here is the link to the Telegram bot](https://t.me/smart_carpark_bot).

## Commands for the Telegram Bot:

| Command syntax                          | Description                                                                                                                                                                                                      | Example          |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| /start                                  | Starts the bot.                                                                                                                                                                                                  | /start           |
| /locate {car plate number with spacing} | Returns the location (carpark lot number) based on the car plate number given. Car plate number must follow the format specified [here](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Singapore). | /locate SGD8888Z |
| /lots                                   | Returns the number of available lots in the carpark.                                                                                                                                                             | /lots            |
| /fee {car plate number with spacing}    | Returns the parking fee of the given carplate.                                                                                                                                                                   | /fee SGD8888Z    |

---

We're excited to see how you'll help us drive the future of smart parking! 🌟

Happy coding! 🚀👩‍💻👨‍💻\
CS3237 Group G05
