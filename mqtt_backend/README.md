# Smart Carpark Backend (MQTT) Codebase 🚗💡

Welcome to the GitHub repository for the Smart Carpark system's centralised MQTT backend.

This is done as part of the Project for CS3237 - Introduction to Internet of Things, AY23/24 Semester 1.

Done by Group 5!

## Repository Structure 🗂️

Here's a guide to what you'll find in this repository:

- `mqtt_backend.py`: Main python script for backend running as MQTT client

- `requirements.txt`: Consists of required packages for `mqtt_backend.py`

## Setup & Installation ⚙️

1. Install [Python 3.0](https://www.python.org/downloads/) (Preferably Python 3.10.12) on your machine.
2. Install MQTT. Start up the service. The broker should be running on port `1883`.

### Initial Setting and Starting Up of MQTT Client Backend

This steps written for Ubuntu and Mac OS.

1. Open your console in `./mqtt_backend`.

```
cd mqtt_backend
```

2. Create Python virtual environment.

```
python3 -m venv venv
```

3. Activate a Python virtual environment.

```
source ./venv/bin/activate
```

4. Install packages.

```
pip install -r requirements.txt
```

5. Run the python script.

```
python3 mqtt_backend.py
```

## Subsequent Starting Up of MQTT Client Backend

This steps written for Ubuntu and Mac OS.

1. Open your console in `./mqtt_backend`.

```
cd mqtt_backend
```

2. Activate a Python virtual environment.

```
source ./venv/bin/activate
```

3. Run the python script.

```
python3 mqtt_backend.py
```

---

We're excited to see how you'll help us drive the future of smart parking! 🌟

Happy coding! 🚀👩‍💻👨‍💻\
CS3237 Group G05
