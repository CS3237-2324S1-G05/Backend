# Smart Carpark Backend (MQTT)

This is the centralised MQTT backend for the smart carpark.

## Setting up

1. Install [Python 3.0](https://www.python.org/downloads/) (Preferably Python 3.10.12) on your machine.
2. Install MQTT. Start up the service. The broker should be running on port `1883`.

### Starting MQTT Backend

For initial setting up, please go through all the steps below. For subsequent runs, you may skip steps.

1. Open your console in `./mqtt_backend`.

```
cd mqtt_backend
```

2. Create Python virtual environment. This step is only for the initial setup. You may skip it in your subsequent runs.

```
python3 -m venv venv
```

3. Activate a Python virtual environment.

```
source ./venv/bin/activate
```

4. Install packages. This step is only for the initial setup. You may skip it in your subsequent runs.

```
pip install -r requirements.txt
```

5. Run the python script.

```
python3 mqtt_backend.py
```
