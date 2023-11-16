# Smart Carpark Backend (Database Flask)

This is the Flask API to the MongoDB database for the smart carpark.
The MongoDB instance is running on MongoDB Atlas.

## Prerequisites

1. Install [Python 3.0](https://www.python.org/downloads/) (Preferably Python 3.10.12) on your machine.

### Initial Setting and Starting Up of MongoDB Flask API

This steps written for Ubuntu and Mac OS.

1. Open your console in `./db`.

```
cd db
```

2. Create Python virtual environment.

```
python3 -m venv venv
```

3. Activate a Python virtual environment.

```
source ./venv/bin/activate
```

4. Load environment variables.

```
source .env
```

5. Install packages.

```
pip install -r requirements.txt
```

6. Run the python script. You can now access via `localhost:6000` or `<your ip>:6000`.

```
python3 flask_db.py
```

## Subsequent Starting Up of MongoDB Flask API

This steps written for Ubuntu and Mac OS.

1. Open your console in `./db`.

```
cd db
```

2. Activate a Python virtual environment.

```
source ./venv/bin/activate
```

3. Load environment variables.

```
source .env
```

4. Run the python script. You can now access via `localhost:6000` or `<your ip>:6000`.

```
python3 flask_db.py
```
