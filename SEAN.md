# README for Sean

## Checklist before starting
- [ ] Ensure can connect internet
- [ ] Ensure can connect to mqtt broker
- [ ] Ensure to connect to VPN
- [ ] Start DB
- [ ] Start Flask Backend
- [ ] Start mqtt-backend
- [ ] Start Telegram Backend
- [ ] Nadine to ping Sean 192.168.43.226
- [ ] Venus to postman Sean 192.168.43.226:3237
- [ ] Turn on everything
- [ ] Venus to delete everything in DB

## Start DB first
```
cd db
source ./venv/bin/activate
source .env
python3 flask_db.py
```

## Start Flask Backend
```
cd flask_backend
source ./venv/bin/activate
sudo python3 flask_backend.py
```

## Start mqtt-backend
```
cd mqtt_backend
source ./venv/bin/activate
python3 mqtt_backend.py
```

## Start Telegram Backend
```
source ./venv/bin/activate
source .env
python3 bot.py
```


## IP Addresses
- Flask Backend: 192.168.43.226:3237
- DB: 192.168.43.226:6000
- mqtt-server: 192.168.43.226:1883