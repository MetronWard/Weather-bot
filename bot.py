import logging
import shelve

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from weather import Weather

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


class Bot:
    """Creates a telegram bot class for interacting with the user"""

    def __init__(self):
        """Initializes the bot with the correct api keys, and a predefined location being Ayeduase"""
        self.location = 'Ayeduase'
        self.keys = shelve.open('keys/api_keys')
        self.telegram_key = self.keys['telegram_api']
        logging.debug(f'Bot Class created with the default location set as {self.location} '
                      f'and an api key of {self.telegram_key}')

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Function to respond to the /start command """
        user = update.effective_user
        await update.message.reply_text('Hiii')
        logging.debug(f'/start command sent by the User')

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        await update.message.reply_text('This is a bot created by Eugene Ward to provide timely weather reports\n'
                                        'Just type in your location and press enter.'
                                        'The weather report for that location would be displayed\n'
                                        'type /forecast to get the weather forecast for the next 6 hours')
        logging.debug(f'/help command sent by the User')

    async def _get_forecast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """This function provides the cleaned up version of the weather data received from the weather class"""
        self.weather = Weather(self.location)
        for item in self.weather.get_forecast():
            await update.message.reply_text(
                f'{item["hour"]}\n'
                f'Condition - {item["condition"]}\n'
                f'Wind Speed - {item["wind_speed"]}\n'
                f'Chance Of rain - {item["rain"]}'
            )
        logging.debug(f'Weather data returned')

    async def post_forecast(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        await self._get_forecast(update=update, context=context)

    async def message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.location = update.message.text
        await update.message.reply_text(f'Current location - {self.location}')
        await self._get_forecast(update=update, context=context)

    def main(self):
        self.application = Application.builder().token(self.telegram_key).build()
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('help', self.help))
        self.application.add_handler(CommandHandler('forecast', self.post_forecast))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message))
        self.application.run_polling()


if __name__ == '__main__':
    bot = Bot()
    bot.main()
