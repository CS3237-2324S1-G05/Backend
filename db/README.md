# Smart Carpark Backend (Database Flask)

This is the Flask API to the MongoDB database for the smart carpark.

## Prerequisites

1. Install [Python 3.0](https://www.python.org/downloads/) (Preferably Python 3.10.12) on your machine.

## Starting up MongoDB Flask API

For initial setting up, please go through all the steps below. For subsequent runs, you may skip steps.

1. Open your console in `./db`.

```
cd db
```

2. Create Python virtual environment. This step is only for the initial setup. You may skip it in your subsequent runs.

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

5. Install packages. This step is only for the initial setup. You may skip it in your subsequent runs.

```
bash ./install.sh
```

6. Run the python script. You can now access via `localhost:6000` or `<your ip>:6000`.

```
python3 flask_db.py
```
