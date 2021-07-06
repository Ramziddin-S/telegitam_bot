from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import (
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
)
from database import Database
from datetime import datetime
import commands
import globals

database = Database("db-bot.db")


def check_user_data(func):
    def inner(update, context):
        chat_id = update.message.from_user.id
        user = database.get_user_by_chat_id(chat_id)
        state = context.user_data.get("state", 0)
        if state == 0 or state == 5:
            if user:
                if not user['first_name']:
                    update.message.reply_text(
                        text="Ismingizni kiritng!",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    context.user_data['state'] = 1
                    return False
                elif not user['last_name']:
                    update.message.reply_text(
                        text="Familiyangizni kiriting!",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    context.user_data['state'] = 2
                    return False
                elif not user['contact']:
                    buttons = [[KeyboardButton(text="Yuborish", request_contact=True)]]
                    update.message.reply_text(
                        text="Telefon raqamingizni kiriting!",
                        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
                    )
                    context.user_data['state'] = 3
                    return False
                else:
                    context.user_data['state'] = 4
                    return func(update, context)
            else:
                first_name = update.message.from_user.first_name
                last_name = update.message.from_user.last_name
                database.create_user(chat_id, first_name, last_name, datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
                buttons = [[KeyboardButton(text="Yuborish", request_contact=True)]]
                update.message.reply_text(
                    text="Telefon raqamingizni kiriting!",
                    reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
                )
                context.user_data['state'] = 1
                return False
        else:
            return func(update, context)
    return inner


def check_user_state(update, context):
    chat_id = update.message.from_user.id
    user = database.get_user_by_chat_id(chat_id)
    if user:
        if not user['first_name']:
            update.message.reply_text(text="Ismingizni kiriting!")
            return 1
        elif not user['last_name']:
            update.message.reply_text(text="Familiyangizni kiriting!")
            return 2
        elif not user['contact']:
            buttons = [[KeyboardButton(text="Yuborish", request_contact=True)]]
            update.message.reply_text(
                text="Telefon raqamingizni kiriting!",
                reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            )
            return 3
        else:
            commands.main_menu(update, context)
            return 4
    else:
        first_name = update.message.from_user.first_name
        last_name = update.message.from_user.last_name
        database.create_user(chat_id, first_name, last_name, datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        update.message.reply_text(text="Telefon raqamingizni kiriting!")
        return 3


@check_user_data
def start_command(update, context):
    commands.main_menu(update, context)


@check_user_data
def message_handler(update, context):
    msg = update.message.text
    chat_id = update.message.from_user.id
    state = context.user_data.get("state", 0)

    if state == 1:
        database.update_user(state, chat_id, msg)
        context.user_data['state'] = check_user_state(update, context)

    elif state == 2:
        database.update_user(state, chat_id, msg)
        context.user_data['state'] = check_user_state(update, context)

    elif state == 3:
        database.update_user(state, chat_id, msg)
        context.user_data['state'] = check_user_state(update, context)

    else:
        if msg == globals.btn_fast_food:
            categories = database.get_all_categorie()
            commands.fast_food(update, context, categories)

        elif msg == globals.btn_card:
            print("Card")
        elif msg == globals.btn_order:
            print("Order")
        else:
            print("Other word!")


def callback_handler(update, context):
    query = update.callback_query
    data_split = query.data.split("_")
    chat_id = query.from_user.id
    message_id = query.message.message_id

    if data_split[0] == "category":
        if data_split[1] == "back":
            categories = database.get_all_categories()
            commands.back_to_fast_food(update, context, categories, chat_id, message_id)

        elif data_split[1] == "product":
            if data_split[2] == "card":
                if len(data_split) > 4:
                    if data_split[4] == "minus":
                        count = int(data_split[5])
                        if count > 1:
                            count -= 1
                        commands.product_amount(update, context, chat_id, message_id, data_split[3], count)

                    elif data_split[4] == "plus":
                        count = int(data_split[5])
                        count += 1
                        commands.product_amount(update, context, chat_id, message_id, data_split[3], count)

                    elif data_split[4] == "submit":
                        pass

                    elif data_split[4] == "back":
                        products = database.get_all_products_by_category(int(data_split[3]))
                        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                        commands.back_to_category_products(update, context, products, chat_id, message_id)

                    elif data_split[4] == "count":
                        pass

                else:
                    commands.product_amount(update, context, chat_id, message_id, data_split[3], 1)

            elif data_split[2] == "back":
                products = database.get_all_products_by_category(int(data_split[3]))
                context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                commands.back_to_category_products(update, context, products, chat_id, message_id)
            else:
                product = database.get_product_by_id(int(data_split[2]))
                commands.send_product(update, context, product, chat_id, message_id)

        else:
            products = database.get_all_products_by_category(int(data_split[1]))
            commands.category_products(update, context, products, chat_id, message_id)


def contact_handler(update, context):
    chat_id = update.message.from_user.id
    contact = update.message.contact.phone_number
    state = context.user_data.get('state', 0)
    if state == 3:
        database.update_user(state, chat_id, contact)
        context.user_data['state'] = check_user_state(update, context)


def main():
    updater = Updater("")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    dispatcher.add_handler(CallbackQueryHandler(callback_handler))
    dispatcher.add_handler(MessageHandler(Filters.contact, contact_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
