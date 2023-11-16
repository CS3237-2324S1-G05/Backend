# Smart Carpark Backend (Flask Backend)

This is the centralised Flask backend for the smart carpark.
It is mainly to communicate with the ESP32 cameras and ML models.

## Prerequisites

1. Install [Python 3.0](https://www.python.org/downloads/) (Preferably Python 3.10.12) on your machine.

### Initial Setting and Starting Up of Backend Flask API

This steps written for Ubuntu and Mac OS.

1. Open your console in `./flask_backend`.

```
cd flask_backend
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

5. Run the python script. You can now access via `localhost:3237` or `<your ip>:3237`.

```
python3 flask_backend.py
```

## Subsequent Starting Up of Backend Flask API

This steps written for Ubuntu and Mac OS.

1. Open your console in `./flask_backend`.

```
cd flask_backend
```

2. Activate a Python virtual environment.

```
source ./venv/bin/activate
```

3. Run the python script. You can now access via `localhost:3237` or `<your ip>:3237`.

```
python3 flask_backend.py
```
