from aiogram.utils.keyboard import ReplyKeyboardBuilder

def reply_keyboard():
    reply_keyboard = ReplyKeyboardBuilder()
    reply_keyboard.button(text='/send_message')
    reply_keyboard.button(text='/pars_users')
    reply_keyboard.button(text='/accs')
    reply_keyboard.button(text='/users')
    reply_keyboard.button(text='/help')
    reply_keyboard.adjust(1, 1, 2, 1)
    return reply_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)

def reply_keyboard_answer():
    reply_keyboard = ReplyKeyboardBuilder()
    reply_keyboard.button(text='Да')
    reply_keyboard.button(text='Нет')
    reply_keyboard.adjust(2)
    return reply_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)

def reply_keyboard_accs():
    reply_keyboard = ReplyKeyboardBuilder()
    reply_keyboard.button(text='/add_acc')
    reply_keyboard.button(text='/enable_acc')
    reply_keyboard.button(text='/disable_acc')
    reply_keyboard.adjust(1, 1, 1)
    return reply_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)