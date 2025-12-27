def register(bot):
    @bot.message_handler(commands=['start', 'help'])
    def start(message):
        bot.send_message(
            message.chat.id,
            "Отправь Excel-файл, и я сформирую отчет 📊"
        )
