import logging
import pwnagotchi.plugins as plugins
import telegram
from pwnagotchi.voice import Voice

class Telegram(plugins.Plugin):
    __author__ = 'ChatGPT'
    __version__ = '1.2.0'
    __license__ = 'GPL3'
    __description__ = 'Chats to telegram'
    __dependencies__ = 'python-telegram-bot==13.15',

    def on_loaded(self):
        logging.info("telegram plugin loaded.")
        self.message_queue = []

    # called when there's internet
    def on_internet_available(self, agent):
        config = agent.config()
        display = agent.view()
        last_session = agent.last_session

        if last_session.is_new() and last_session.handshakes > 0:
            try:
                logging.info("Connecting to Telegram...")

                bot = telegram.Bot(self.options['bot_token'])

                # Attempt to send each message in the queue
                for message in self.message_queue:
                    try:
                        bot.sendMessage(chat_id=self.options['chat_id'], text=message, disable_web_page_preview=True)
                        logging.info("telegram: message sent from queue: %s" % message)
                    except Exception:
                        logging.exception("Error while sending on Telegram from queue")

                # Clear the queue after attempting to send messages
                self.message_queue = []

                message = Voice(lang=config['main']['lang']).on_last_session_tweet(last_session)
                if self.options['send_message'] is True:
                    bot.sendMessage(chat_id=self.options['chat_id'], text=message, disable_web_page_preview=True)
                    logging.info("telegram: message sent: %s" % message)

                picture = '/root/pwnagotchi.png'
                display.on_manual_mode(last_session)
                display.image().save(picture, 'png')
                display.update(force=True)

                if self.options['send_picture'] is True:
                    bot.sendPhoto(chat_id=self.options['chat_id'], photo=open(picture, 'rb'))
                    logging.info("telegram: picture sent")

                last_session.save_session_id()
                display.set('status', 'Telegram notification sent!')
                display.update(force=True)
            except Exception:
                # If sending fails, add the message to the queue
                self.message_queue.append(message)
                logging.exception("Error while sending on Telegram, added to queue")

    def on_handshake(self, agent, filename, access_point, client_station):
        config = agent.config()
        display = agent.view()

        try:
            logging.info("Connecting to Telegram...")

            bot = telegram.Bot(self.options['bot_token'])

            message = "New handshake captured: {} - {}".format(access_point['hostname'], client_station['mac'])
            if self.options['send_message'] is True:
                bot.sendMessage(chat_id=self.options['chat_id'], text=message, disable_web_page_preview=True)
                logging.info("telegram: message sent: %s" % message)

            display.set('status', 'Telegram notification sent!')
            display.update(force=True)
        except Exception:
            # If sending fails, add the message to the queue
            self.message_queue.append(message)
            logging.exception("Error while sending on Telegram, added to queue")
