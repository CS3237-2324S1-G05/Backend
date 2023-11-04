# Smart Carpark Backend (MQTT)

This is the centralised MQTT backend for the smart carpark.

## Setting up

1. Install [Python 3.0](https://www.python.org/downloads/) (Preferably Python 3.10.12) on your machine.
2. Install MQTT. Start up the service. The broker should be running on port `1883`.

### Setting up and starting backend API

For initial setting up, please go through all the steps below.

1. Open your console in `./mqtt_backend`. Activate a Python virtual environment.

```
python3 -m venv venv
source ./venv/bin/activate
```

2. Load environment variables.

```
source .env
```

3. Install packages.

```
bash ./install.sh
```

4. Run the python MQTT backend script.

```
python3 mqtt_backend.py
```

## Additional Information

### Done For

Made for AY23/24 Semester 1 CS3237 Project.
Done by Group 5.
