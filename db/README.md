# Smart Carpark Backend (Flask Database) Codebase 🚗💡

Welcome to the GitHub repository for the Smart Carpark system's Flask API endpoints to the MongoDB database.
The MongoDB instance is running on MongoDB Atlas.

This is done as part of the Project for CS3237 - Introduction to Internet of Things, AY23/24 Semester 1.

Done by Group 5!

## Repository Structure 🗂️

Here's a guide to what you'll find in this repository:

- `.env`: Consists of username and password for MongoDB Atlas

- `constants.py`: Constants file for `flask_db.py`

- `flask_db.py`: Main python script for Flask that interacts with MongoDB Atlas

- `mongodb_class.py`: Class used by `flask_db.py` to interact with MongoDB Atlas

- `requirements.txt`: Consists of required packages for `flask_db.py`

## Setup & Installation ⚙️

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

---

We're excited to see how you'll help us drive the future of smart parking! 🌟

Happy coding! 🚀👩‍💻👨‍💻\
CS3237 Group G05
