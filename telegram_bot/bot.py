"""
CS3237 Project Group 5 Telegram Bot
Written by Venus Lim
Carplate format (from https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Singapore)
"""

import re
import requests
import os
import math
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler

import constants

class TelegramBot:
  def __init__(self, token):
    self.builder = ApplicationBuilder().token(token).build()

  # For user to start the bot / print start message
  async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.message.from_user.username
    await update.message.reply_text(f'Hello {username}, welcome to Smart Carpark!\n' + 
                                    'Enter / to see the available commands.')

  def is_car_plate_valid(self, car_plate):
    pattern = r'^S[A-HJ-NP-TV-Z]{2}[1-9][0-9]{0,3}(?<!0)[A-EG-HJ-MP-TV-Z]?$'
    if re.match(pattern, car_plate):
      return True
    else:
      return False
  
  def get_car_location(self, car_plate):
    url = f'http://{constants.FLASK_BACKEND_IP}:{constants.FLASK_BACKEND_PORT}{constants.DB_GET_CAR_LOT_ENDPOINT}'
    url += f'?data={car_plate}'
    try:
      response = requests.get(url)
      if response.status_code == constants.SUCCESS_STATUS_CODE:
        data = response.json()
        lot = data['result']
        print(f'Car {car_plate} is at lot {lot}')
        return 'The location of car ' + str(car_plate) + ' is: LOT ' + str(lot)
      else:
        error_msg = response.json()['error']
        print(f'Error {response.status_code}: {error_msg}')
        return 'Unable to get location of car.'
    except requests.exceptions.ConnectionError as e:
      print('Error:', e)
      return 'Unable to get location of car.'
    
  async def locate(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
      await update.message.reply_text('Please enter using the following syntax: /locate {carplate number with no spacing}')
    else:
      car_plate = context.args[0].upper()
      if self.is_car_plate_valid(car_plate):
        await update.message.reply_text(self.get_car_location(car_plate))
      else:
        await update.message.reply_text(f'Invalid car plate number.')
        
  async def available_lot_count(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = f'http://{constants.FLASK_BACKEND_IP}:{constants.FLASK_BACKEND_PORT}{constants.DB_GET_NUMBER_OF_AVAILABLE_LOTS_ENDPOINT}'
    try:
      response = requests.get(url)
      if response.status_code == constants.SUCCESS_STATUS_CODE:
        count = response.json()['result']
        print(f'Available lot count: {count}')
        if count > 1:
          await update.message.reply_text(f'There are {count} available lots.')
        else:
          await update.message.reply_text(f'There is {count} available lot.')
      else:
        error_msg = response.json()['error']
        print(f'Error {response.status_code}: {error_msg}')
        await update.message.reply_text('Unable to get available lot count.')
    except requests.exceptions.ConnectionError as e:
      print('Error:', e)
      await update.message.reply_text('Unable to get available lot count.')
      
  def get_fee(self, entrance_time):
    entrance_time = datetime.strptime(entrance_time, "%a, %d %b %Y %H:%M:%S %Z")
    current_time = datetime.utcnow()
    time_difference = (current_time - entrance_time).total_seconds()
    print(f'Car entered at {entrance_time}, current time is {current_time}, time difference is {time_difference}')
    parking_fee = 0
    if time_difference > 120:
      # Charge if exceed 2 minutes, Rounded up the hour, 1h = $2.5
      parking_duration = math.ceil(time_difference / 3600)
      parking_fee = "{:.2f}".format(round(parking_duration * 2.5, 2))
    print(f'Parking fee is ${parking_fee}')
    return parking_fee
      
  def get_fee_msg(self, car_plate):
    url = f'http://{constants.FLASK_BACKEND_IP}:{constants.FLASK_BACKEND_PORT}{constants.DB_GET_LAST_ENTRY_TIME_ENDPOINT}'
    url += f'?data={car_plate}'
    return_error_msg = 'Unable to calculate parking fee.'
    try:
      response = requests.get(url)
      if response.status_code == constants.SUCCESS_STATUS_CODE:
        data = response.json()
        entrance_time = data['result']
        if entrance_time is None:
          return return_error_msg
        else:
          fee = self.get_fee(entrance_time)
          return f'The parking fee for car {car_plate} is ${fee}.'
      else:
        error_msg = response.json()['error']
        print(f'Error {response.status_code}: {error_msg}')
        return return_error_msg
    except requests.exceptions.ConnectionError as e:
      print('Error:', e)
      return return_error_msg
  
  async def fee(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
      await update.message.reply_text('Please enter using the following syntax: /fee {carplate number with no spacing}')
    else:
      car_plate = context.args[0].upper()
      if self.is_car_plate_valid(car_plate):
        await update.message.reply_text(self.get_fee_msg(car_plate))
      else:
        await update.message.reply_text(f'Invalid car plate number.')
        
  # For unknown inputs
  async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = ['/start', '/locate', '/lots', '/fee']
    message = 'Sorry, I didn\'t understand that.\nHere are the available commands:\n' + '\n'.join(commands)
    await update.message.reply_text(message)

if __name__ == '__main__':
  # Initialise bot
  bot_token = os.environ.get('BOT_TOKEN')
  bot = TelegramBot(bot_token)

  # Add handlers for the different commands
  bot.builder.add_handler(CommandHandler('start', bot.start))
  bot.builder.add_handler(CommandHandler('locate', bot.locate))
  bot.builder.add_handler(CommandHandler('lots', bot.available_lot_count))
  bot.builder.add_handler(CommandHandler('fee', bot.fee))
  bot.builder.add_handler(MessageHandler(None, bot.unknown))

  # Start polling
  print(f'Bot starts polling...')
  bot.builder.run_polling()
