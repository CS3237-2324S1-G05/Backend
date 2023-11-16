# Smart Carpark Backend (MQTT)

This is the centralised MQTT backend for the smart carpark.

## Prerequisites

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
