# Smart Carpark Backend (Flask Backend)

This is the centralised Flask backend for the smart carpark.

## Prerequisites

1. Install [Python 3.0](https://www.python.org/downloads/) (Preferably Python 3.10.12) on your machine.

### Starting up Backend Flask API

For initial setting up, please go through all the steps below. For subsequent runs, you may skip steps.

1. Open your console in `./flask_backend`.

```
cd flask_backend
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

5. Run the python script. You can now access via `localhost:7000` or `<your ip>:7000`.

```
python3 flask_backend.py
```
