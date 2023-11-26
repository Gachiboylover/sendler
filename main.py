import asyncio
import random
import logging
import os


from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from opentele.tl import TelegramClient
from opentele.tl.telethon import utils, types
from telethon.errors import UserDeactivatedBanError,PeerFloodError,FloodWaitError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from dotenv import load_dotenv
from openpyxl import Workbook

from Commands import set_commands
from Keyboards import reply_keyboard, reply_keyboard_accs, reply_keyboard_answer 
from DataBase import DataBase

logger = logging.FileHandler(filename="info.log")
logging.basicConfig(level=logging.INFO,filename="info.log",filemode='w')

DB = DataBase()


def check(mes):
    try:
        mes = mes.strip().split(' ')
        return len(mes) == 4
    except Exception:
        return False


class StepsForm(StatesGroup):
    GET_ANSWER = State()
    GET_FLAG = State()
    GET_EN = State()
    GET_DIS = State()
    GET_URL = State()
    GET_MES = State()
    
    
async def get_start(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}.\n"/help"- получи помощь.', reply_markup=reply_keyboard())


async def get_help(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}.\n"/add_acc" - загрузи сессию.\n"/enable_acc" - сделай аккаунт активным.\n"/disable" - сделай аккаунт неактивным.\n"/pars_users" - спарси пользователей.\n"/send_message" - начни рассылку.\n"/users" - данные о пользователях(xlsx).\n"/enable_users" - сделай всех пользователей активными для рассылки.\nВАЖНОЕ! При парсинге следите за тем, чтобы бот был в канале, и чтобы канал был открытым.', reply_markup=reply_keyboard())
    global client
    await client.disconnect()
    
async def get_users(message: Message, bot: Bot):
    wb = Workbook()
    ws = wb.active
    all_users = DB.db_get_all_users()
    for row in all_users:
        ws.append(row)
    wb.save('users.xlsx')
    doc = FSInputFile('users.xlsx')
    await bot.send_document(message.from_user.id, doc)
    ws.delete_rows(1, len(ws['A']))
    wb.save('users.xlsx')

async def get_accs(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, f'Выбери действие.', reply_markup=reply_keyboard_accs())       


async def get_add_acc(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(message.from_user.id, f'Введите данные вида(через пробел): phone password api_id api_hash')
    await state.set_state(StepsForm.GET_FLAG)

async def get_add_acc_flag(message: Message, bot: Bot, state: FSMContext):
    try:
        if check(message.text):
            await state.update_data(name=message.text)
            await bot.send_message(message.from_user.id, f'Вы уверены?', reply_markup=reply_keyboard_answer())
            await state.set_state(StepsForm.GET_ANSWER)
        else:
            await bot.send_message(message.from_user.id, 'Извините, данные введины неверно, попробуйте снова. ', reply_markup=reply_keyboard())
            await state.clear()
    except Exception:
        await bot.send_message(message.from_user.id, 'Извините, данные введины неверно, попробуйте снова. ', reply_markup=reply_keyboard())
        await state.clear()
        
async def get_add_acc_answer(message: Message, bot: Bot, state: FSMContext):
    try:
        if message.text == 'Да':
            context_data = await state.get_data()
            acc_info = context_data['name'].split(' ')
            phone = acc_info[0]
            password = acc_info[1]
            api_id = acc_info[2]
            api_hash = acc_info[3]
            session = f'sessions/{phone}.session'
            try:
                client = TelegramClient(session=session, api_id=api_id, api_hash=api_hash, system_version='4.16.30-vxCUSTOM')
                await client.start(phone, password=password)
                DB.db_add_acc(phone, api_id, api_hash)
                await bot.send_message(message.from_user.id, f'Готово!', reply_markup=reply_keyboard() )
                await state.clear()
            except Exception:
                await bot.send_message(message.from_user.id, f'Проверьте корректность введённых данных.', reply_markup=reply_keyboard() )
                await state.clear()
        else:
            await bot.send_message(message.from_user.id, 'Отмененно.', reply_markup=reply_keyboard())
            await state.clear()
    except Exception:
        await bot.send_message(message.from_user.id, 'Отмененно.', reply_markup=reply_keyboard())
        await state.clear()


async def get_en_acc(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(message.from_user.id, f'Выберете номер аккаунта: ')
    await bot.send_message(message.from_user.id, '\n'.join(f'{c+1}. {v[0]}' for c, v in enumerate(DB.db_show_all_accs())))
    await state.update_data(name=DB.db_show_all_accs())
    await state.set_state(StepsForm.GET_EN)

async def get_en_acc_answer(message: Message, bot: Bot, state: FSMContext):
    try:
        context_data = await state.get_data()
        phone = context_data['name'][int(message.text)-1][0].strip()
        DB.db_change_acc_state(phone, 1)
        await bot.send_message(message.from_user.id, f'Готово!', reply_markup=reply_keyboard() )
        await state.clear()
    except Exception:
        await bot.send_message(message.from_user.id, f'Ошибка', reply_markup=reply_keyboard() )
        await state.clear()
    
    
async def get_dis_acc(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(message.from_user.id, f'Выберете номер аккаунта: ')
    await bot.send_message(message.from_user.id, '\n'.join(f'{c+1}. {v[0]}' for c, v in enumerate(DB.db_show_all_accs())))
    await state.update_data(name=DB.db_show_all_accs())
    await state.set_state(StepsForm.GET_DIS)

async def get_dis_acc_answer(message: Message, bot: Bot, state: FSMContext):
    try:
        context_data = await state.get_data()
        phone = context_data['name'][int(message.text)-1][0].strip()
        DB.db_change_acc_state(phone, 0)
        await bot.send_message(message.from_user.id, f'Готово!', reply_markup=reply_keyboard() )
        await state.clear()
    except Exception:
        await bot.send_message(message.from_user.id, f'Ошибка', reply_markup=reply_keyboard() )
        await state.clear()
        
        
async def get_pars_users(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(message.from_user.id, f'Введите ссылку на канал ...  ')
    await state.set_state(StepsForm.GET_URL)

async def get_pars_users_answer(message: Message, bot: Bot, state: FSMContext):
    try:
        url = message.text
        accs = DB.db_get_all_accs()
        if len(accs) == 0:
            await bot.send_message(message.from_user.id, 'Нет аккаунтов, или нет активных аккаунтов. ', reply_markup=reply_keyboard())
        else:
            RandAcc:tuple = random.choice(accs)
            phone = RandAcc[1]
            api_id = RandAcc[2]
            api_hash = RandAcc[3]
            session = f'sessions/{phone}.session'
            global client
            client = TelegramClient(session=session, api_id=api_id, api_hash=api_hash, system_version='4.16.30-vxCUSTOM')
            await client.connect()
            await bot.send_message(message.from_user.id, f'Выбран аккаунт: {phone}. ')
            channel = await client.get_entity(url)
            try:
                await client(JoinChannelRequest(channel))
            except Exception as ex:
                print(ex)
            query_list = list()
    except Exception:
        await bot.send_message(message.from_user.id, f'Проверьте ссылку, и состоит ли пользователь в группе. ', reply_markup=reply_keyboard())
        await state.clear()
        logging.error(ex,exc_info=True)
        await client.disconnect()
    await state.clear()
    try:
        print(1)
        iter_mes = client.iter_messages(channel)
        print(2)
        all_id = DB.db_get_all_users_ids()
        async for mes in iter_mes:
            print(mes.from_id.user_id)
            #user:utils.types.User = user
            #if not user.bot and not user.deleted and user.id not in all_id:
            if mes.from_id not in all_id:
                    try:
                        user = await client(GetFullUserRequest(int(mes.from_id.user_id)))
                    except Exception:
                        continue 
                    print(user)
                    user = user.users
                    #user = await client.get_entity(mes.from_id)
                    print(user)
                    #id_ = user.id
                    #username = user.username if user.username else ''
                    #fn = user.first_name
                    #ln = user.last_name if user.last_name else ''
                    #hash = user.access_hash
                    #phone = user.phone if user.phone else ''
                    #query_list.append((id_,username,hash,fn,ln,phone,url,1))
        if len(query_list) > 0:
            DB.db_add_users(query_list)
        await client.disconnect()
        await bot.send_message(message.from_user.id, f'Парсинг завершен! Получена информация о {len(query_list)} пользователей', reply_markup=reply_keyboard())
        await state.clear()
    except Exception as ex:
        print(ex)
        await bot.send_message(message.from_user.id, f'Проверьте чтобы это был открытый канал. ', reply_markup=reply_keyboard())
        await client.disconnect()
        await state.clear()
    await state.clear()

async def get_enable_all_users(message: Message, bot: Bot):
    DB.db_enable_all_users()
    await bot.send_message(message.from_user.id, f'Все пользователи теперь доступны для рассылки. ', reply_markup=reply_keyboard())

async def get_send_message(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(message.from_user.id, f'Введите сообщение: ')
    await state.set_state(StepsForm.GET_MES)

async def get_send_message_answer(message: Message, bot: Bot, state: FSMContext):
    try:
        en = message.entities
        mes = message.text
        flen = 0
        try:
            for c, e in enumerate(en):
                if e.type == 'text_link':
                    length = e.length
                    off = int(e.offset)
                mes = mes.replace(mes[off+flen:off+length+flen], f'[{mes[off+flen:off+length+flen]}]({e.url})')
                flen+=4+len(e.url)
        except Exception as ex:
            print(ex)
        print(mes)
        accs = DB.db_get_all_accs()
        all_name = DB.db_get_all_users_name()
        amount_send_messages = 0
        if len(accs) == 0:
            await bot.send_message(message.from_user.id, 'Нет аккаунтов, или нет активных аккаунтов. ', reply_markup=reply_keyboard())
        else:
            await bot.send_message(message.from_user.id, 'Рассылка началась. ', reply_markup=reply_keyboard())
            for account in accs:
                try:
                    session = f"sessions/{account[1]}.session"
                    client = TelegramClient(session=session, api_id=account[2], api_hash=account[3], system_version='4.16.30-vxCUSTOM')
                    await client.connect()
                    trys = 3
                    trys_ = 3
                    for name in all_name:
                        try:
                            if name in all_name:
                                await client.send_message(f'@{name}', mes, parse_mode='markdown')
                                amount_send_messages += 1
                                DB.db_change_user_state(name)
                                all_name.remove(name)
                                print(f"отправлено сообщение пользователю: @{name}")
                                await asyncio.sleep(random.randint(30, 90))
                        except FloodWaitError:
                            await bot.send_message(message.from_user.id, 'К сожалению аккаунт не сможет отправлять сообщения какое-то время...', reply_markup=reply_keyboard())
                            await bot.send_message(message.from_user.id, f'Смена аккаунта {account[1]}')
                            await client.disconnect()
                            await asyncio.sleep(1.5)
                            break
                        except PeerFloodError:
                            await bot.send_message(message.from_user.id, 'Было произведено слишком много запросов (при отправлении сообщений) осталось {trys} попыток. ', reply_markup=reply_keyboard())
                            trys-=1
                            if trys<=0:
                                await bot.send_message(message.from_user.id, f'Смена аккаунта {account[1]}', reply_markup=reply_keyboard())
                                await asyncio.sleep(1.5)
                                break
                        except UserDeactivatedBanError:
                            await bot.send_message(message.from_user.id, f'Аккаунт {account[1]} был заблокирован или взломан!', reply_markup=reply_keyboard())
                            await bot.send_message(message.from_user.id, f'Смена аккаунта {account[1]}')
                            await client.disconnect()
                            logging.exception("The user has been deleted/deactivated")
                            break
                        except Exception as ex:
                            print(ex)
                            await bot.send_message(message.from_user.id, f'Не удалось отправить сообщение пользователю {id_}, осталось {trys_} попыток.', reply_markup=reply_keyboard())
                            print(f'Не удалось отправить сообщение пользователю @{name}, осталось {trys_} попыток.', reply_markup=reply_keyboard())
                            trys_-=1
                            await asyncio.sleep(5.5)
                            if trys<=0:
                                await bot.send_message(message.from_user.id, f'Смена аккаунта {account[1]}', reply_markup=reply_keyboard())
                                await client.disconnect()
                                logging.exception(ex,exc_info=True)
                                break
                except Exception as ex:
                    await bot.send_message(message.from_user.id, f'Не удалось подключиться к аккаунту {account[1]}, Пробую следующий..', reply_markup=reply_keyboard())
                    logging.warning(ex,exc_info=True)
            await bot.send_message(message.from_user.id, f'Рассылка завершена, было отправлено: {amount_send_messages} сообщений пользователям!', reply_markup=reply_keyboard())
    except Exception as ex:
        print(ex)
        await bot.send_message(message.from_user.id, f'Ошибка', reply_markup=reply_keyboard() )
    await state.clear()    
    

async def start():
    load_dotenv()
    bot = Bot(token=os.getenv('TG_API'))
    
    
    dp = Dispatcher()
    dp.startup.register(set_commands)
    dp.message.register(get_start, Command(commands=['start']))
    dp.message.register(get_help, Command(commands=['help']))
    dp.message.register(get_accs, Command(commands=['accs']))
    dp.message.register(get_enable_all_users, Command(commands=['enable_users']))
    dp.message.register(get_users, Command(commands=['users']))
    dp.message.register(get_add_acc, Command(commands=['add_acc']))
    dp.message.register(get_add_acc_flag, StepsForm.GET_FLAG)
    dp.message.register(get_add_acc_answer, StepsForm.GET_ANSWER)
    dp.message.register(get_en_acc, Command(commands=['enable_acc']))
    dp.message.register(get_en_acc_answer, StepsForm.GET_EN)
    dp.message.register(get_dis_acc, Command(commands=['disable_acc']))
    dp.message.register(get_dis_acc_answer, StepsForm.GET_DIS)
    dp.message.register(get_pars_users, Command(commands=['pars_users']))
    dp.message.register(get_pars_users_answer, StepsForm.GET_URL)
    dp.message.register(get_send_message, Command(commands=['send_message']))
    dp.message.register(get_send_message_answer, StepsForm.GET_MES)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        
if __name__ == '__main__':
    asyncio.run(start())