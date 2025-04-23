import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Состояния для ConversationHandler
ADDING, REMOVING = range(2)

cafe_list = []

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Я помогу выбрать кафе для посещения.\n"
        "Команды:\n"
        "/list - показать список кафе\n"
        "/add - добавить кафе\n"
        "/remove - удалить кафе\n"
        "/suggest - предложить кафе\n"
        "/cancel - отменить текущее действие"
    )

def list_cafes(update: Update, context: CallbackContext):
    if not cafe_list:
        update.message.reply_text("Список кафе пуст.")
    else:
        msg = "Список кафе:\n" + '\n'.join(f"{i+1}. {name}" for i, name in enumerate(cafe_list))
        update.message.reply_text(msg)

def add_start(update: Update, context: CallbackContext):
    update.message.reply_text("Напиши название кафе, которое хочешь добавить:")
    return ADDING

def add_cafe(update: Update, context: CallbackContext):
    cafe = update.message.text.strip()
    if cafe:
        cafe_list.append(cafe)
        update.message.reply_text(f"Кафе '{cafe}' добавлено.")
    else:
        update.message.reply_text("Название не может быть пустым. Попробуй снова.")
        return ADDING
    return ConversationHandler.END

def remove_start(update: Update, context: CallbackContext):
    if not cafe_list:
        update.message.reply_text("Список кафе пуст, удалять нечего.")
        return ConversationHandler.END
    msg = "Выбери номер кафе для удаления:\n" + '\n'.join(f"{i+1}. {name}" for i, name in enumerate(cafe_list))
    update.message.reply_text(msg)
    return REMOVING

def remove_cafe(update: Update, context: CallbackContext):
    try:
        index = int(update.message.text) - 1
        if 0 <= index < len(cafe_list):
            removed = cafe_list.pop(index)
            update.message.reply_text(f"Кафе '{removed}' удалено.")
        else:
            update.message.reply_text("Неверный номер. Попробуй снова.")
            return REMOVING
    except ValueError:
        update.message.reply_text("Пожалуйста, отправь номер цифрой.")
        return REMOVING
    return ConversationHandler.END

def suggest(update: Update, context: CallbackContext):
    if not cafe_list:
        update.message.reply_text("Список кафе пуст. Добавь кафе, прежде чем просить предложение.")
    else:
        choice = random.choice(cafe_list)
        update.message.reply_text(f"Сегодня предлагаю пойти в кафе: {choice}")

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Отмена действия.")
    return ConversationHandler.END

def main():
    TOKEN = "7631711179:AAHqF7XSpUAkJ_eyMSAcS1qrFvIPRbWOtNs"  # Вставьте сюда токен вашего бота Telegram

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("list", list_cafes))
    dp.add_handler(CommandHandler("suggest", suggest))

    add_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_start)],
        states={ADDING: [MessageHandler(Filters.text & ~Filters.command, add_cafe)]},
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(add_handler)

    remove_handler = ConversationHandler(
        entry_points=[CommandHandler('remove', remove_start)],
        states={REMOVING: [MessageHandler(Filters.text & ~Filters.command, remove_cafe)]},
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(remove_handler)

    dp.add_handler(CommandHandler('cancel', cancel))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()