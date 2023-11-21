# Smart Carpark Backend (Flask Backend) Codebase 🚗💡

Welcome to the GitHub repository for the Smart Carpark system's centralised Flask backend.
It is mainly to communicate with the ESP32 cameras and ML models.

This is done as part of the Project for CS3237 - Introduction to Internet of Things, AY23/24 Semester 1.

Done by Group 5!

## Repository Structure 🗂️

Here's a guide to what you'll find in this repository:

- `flask_backend.py`: Main python script for backend running on Flask

- `requirements.txt`: Consists of required packages for `flask_backend.py`

## Setup & Installation ⚙️

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

---

We're excited to see how you'll help us drive the future of smart parking! 🌟

Happy coding! 🚀👩‍💻👨‍💻\
CS3237 Group G05
