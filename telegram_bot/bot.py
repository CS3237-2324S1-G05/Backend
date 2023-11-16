"""
CS3237 Project Group 5 Telegram Bot
Written by Venus Lim
Returns the location of a car based on its carplate number; Usage: /where {carplate number}
Carplate format (from https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Singapore)
Also returns the number of available lots in the carpark; Usage: /available_lot_count
"""

import re
import requests
import os
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
                                    'Please enter your carplate number using the following syntax to get your car\'s location: /where {carplate number}')

  # For user to find their car location
  def is_car_plate_valid(self, car_plate):
    pattern = r'^S[A-HJ-NP-TV-Z]{2}[1-9][0-9]{0,3}(?<!0)[A-EG-HJ-MP-TV-Z]?$'
    if re.match(pattern, car_plate):
      return True
    else:
      return False
    
  def get_car_location(self, car_plate):
    url = f'http://{constants.FLASK_BACKEND_IP}:{constants.FLASK_BACKEND_PORT}/db-backend/get-car-lot'
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
    
  async def where(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
      await update.message.reply_text('Please enter using the following syntax: /where {carplate number with no spacing}')
    else:
      car_plate = context.args[0].upper()
      if self.is_car_plate_valid(car_plate):
        await update.message.reply_text(self.get_car_location(car_plate))
      else:
        await update.message.reply_text(f'Invalid car plate number.')
        
  async def available_lot_count(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = f'http://{constants.FLASK_BACKEND_IP}:{constants.FLASK_BACKEND_PORT}/db-backend/get-number-of-available-lots'
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
  
  # For unknown inputs
  async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = ['/start', '/where', '/available_lot_count']
    message = 'Sorry, I didn\'t understand that.\nHere are the available commands:\n' + '\n'.join(commands)
    await update.message.reply_text(message)

if __name__ == '__main__':
  # Initialise bot
  bot_token = os.environ.get('BOT_TOKEN')
  bot = TelegramBot(bot_token)

  # Add handlers for the different commands
  bot.builder.add_handler(CommandHandler('start', bot.start))
  bot.builder.add_handler(CommandHandler('where', bot.where))
  bot.builder.add_handler(CommandHandler('available_lot_count', bot.available_lot_count))
  bot.builder.add_handler(MessageHandler(None, bot.unknown))

  # Start polling
  print(f'Bot starts polling...')
  bot.builder.run_polling()
