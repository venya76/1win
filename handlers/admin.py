from aiogram import F, Router, types, Bot
from aiogram.filters.command import CommandStart
from keyboards.admin import admin_command, get_mailing_type_keyboard
from database.db import DataBase
from aiogram.fsm.context import FSMContext
from database.db import DataBase
from config import ADMIN_ID
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.state import State, StatesGroup
class Admin_States(StatesGroup):

    get_userinfo = State()
    give_balance = State()
    

    get_userinfo_del = State()
    delete_balance = State()


    mailing_type = State()
    mailing_text = State()

router = Router()

@router.message(F.text == '/admin')
async def admin_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await state.clear()
        users_count = await DataBase.get_users()
        money_list = await DataBase.get_users()
        money_count = 0

        await message.answer("Добро пожаловать", reply_markup=await admin_command(), parse_mode="HTML")

@router.callback_query(F.data == 'stat')
async def statistics_handler(callback: types.CallbackQuery):
    users_count = await DataBase.get_users_count()
    verified_count = await DataBase.get_verified_users_count()
    
    # Подсчет пользователей с депозитом и без
    users = await DataBase.get_users()
    deposit_count = 0
    no_deposit_count = 0
    
    # Словарь для хранения языков и их названий
    languages = {
        'ru': 'Русский',
        'en': 'Английский',
        'hi': 'Хинди',
        'br': 'Бразилия',
        'es': 'Испанский',
        'uz': 'Узбекский',
        'az': 'Азербайджанский',
        'tr': 'Турецкий',
        'pt': 'Португальский',
        'ar': 'Арабский'
    }
    
    # Инициализация счетчиков для каждого языка
    lang_counts = {code: 0 for code in languages.keys()}
    
    # Если вы хотите учитывать языки, не указанные в списке, можно добавить дополнительный счетчик
    other_lang_count = 0
    
    for user in users:
        user_id = user[1]  # Предполагается, что user[1] это ID пользователя
        deposit_status = await DataBase.get_deposit_status(user_id)
        if deposit_status == 'dep':
            deposit_count += 1
        else:
            no_deposit_count += 1
        
        # Получение языка пользователя
        # Предполагается, что user[2] содержит информацию о языке
        # Измените индекс, если поле lang находится в другом месте
        lang = user[2].lower() if user[2] else 'unknown'
        if lang in lang_counts:
            lang_counts[lang] += 1
        else:
            other_lang_count += 1
    
    # Формирование строк для каждого языка
    language_stats = ""
    for code, name in languages.items():
        count = lang_counts.get(code, 0)
        language_stats += f"• <b>{name} ({code})</b>: <code>{count}</code>\n"
    
    # (Необязательно) Добавление строки для других языков
    if other_lang_count > 0:
        language_stats += f"• <b>Другие языки</b>: <code>{other_lang_count}</code>\n"
    
    statistics_message = (
        f"<b>📊 Статистика бота:</b>\n\n"
        f"👥 <b>Общее количество пользователей:</b> <code>{users_count}</code>\n"
        f"✅ <b>Верифицированных пользователей:</b> <code>{verified_count}</code>\n"
        f"💰 <b>Пользователей с депозитом:</b> <code>{deposit_count}</code>\n"
        f"❌ <b>Пользователей без депозита:</b> <code>{no_deposit_count}</code>\n\n"
        f"<b>🌐 Статистика по языкам:</b>\n"
        f"{language_stats}"
    )
    await callback.message.answer(statistics_message, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == 'mailing')
async def choose_mailing_type(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("Выберите тип рассылки:", reply_markup=await get_mailing_type_keyboard())
    await state.set_state(Admin_States.mailing_type)

@router.callback_query(F.data.startswith('mailing_'))
async def set_mailing_type(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'decline_mailing':
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer("Рассылка отменена", reply_markup=await admin_command())
        await state.clear()
        return

    mailing_type = callback.data
    await state.update_data(mailing_type=mailing_type)
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("Отправьте сообщение для рассылки:")
    await state.set_state(Admin_States.mailing_text)
    await callback.answer()

@router.message(Admin_States.mailing_text)
async def mailing_state(message: types.Message, state: FSMContext, bot: Bot):
    mailing_message = message.message_id
    ikb = InlineKeyboardBuilder()
    ikb.button(text='Отправить', callback_data='send_mailing')
    ikb.button(text='Отмена', callback_data='decline_mailing')
    ikb.adjust(2)
    
    await bot.copy_message(
        chat_id=message.chat.id,
        from_chat_id=message.chat.id,
        message_id=mailing_message,
        reply_markup=ikb.as_markup(),
        parse_mode="HTML"
    )
    await state.update_data(msg=mailing_message)

@router.callback_query(F.data == 'send_mailing')
async def mailing_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    mailing_message = data['msg']
    mailing_type = data['mailing_type']
    
    errors_count = 0
    good_count = 0
    users = await DataBase.get_users()
    filtered_users = []


    for user in users:
        user_id = user[1]
        verified_status = await DataBase.get_verified_status(user_id)
        deposit_status = await DataBase.get_deposit_status(user_id)

        if mailing_type == 'mailing_all':
            filtered_users.append(user)
        elif mailing_type == 'mailing_verified' and verified_status == 'verifed':
            filtered_users.append(user)
        elif mailing_type == 'mailing_deposit' and deposit_status == 'dep':
            filtered_users.append(user)
        elif mailing_type == 'mailing_new' and verified_status == 'verifed' and deposit_status == 'nedep':
            filtered_users.append(user)
        elif mailing_type == 'mailing_unverified_nodep' and verified_status == '0' and deposit_status == 'nedep':
            filtered_users.append(user)

    try:
        await callback.message.delete()
    except:
        pass
    
    status_message = await callback.message.answer("Рассылка начата...")

    for user in filtered_users:
        try:
            await bot.copy_message(
                chat_id=user[1],
                from_chat_id=callback.from_user.id,
                message_id=mailing_message,
                parse_mode="HTML"
            )
            good_count += 1
        except Exception as ex:
            errors_count += 1
            print(ex)

    mailing_types_desc = {
        'mailing_all': 'всем пользователям',
        'mailing_verified': 'верифицированным пользователям',
        'mailing_deposit': 'пользователям с депозитом',
        'mailing_new': 'неверифицированным пользователям без депозита',
        'mailing_unverified_nodep': 'неверифицированным пользователям без депозита'
    }

    result_message = (
        f"📊 <b>Результаты рассылки {mailing_types_desc[mailing_type]}:</b>\n\n"
        f"✅ <b>Успешно доставлено:</b> <code>{good_count}</code>\n"
        f"❌ <b>Ошибок доставки:</b> <code>{errors_count}</code>"
    )

    try:
        await status_message.delete()
    except:
        pass

    await callback.message.answer(result_message, parse_mode="HTML", reply_markup=await admin_command())
    await state.clear()
@router.callback_query(F.data == 'decline_mailing')
async def decline_mailing(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("Рассылка отменена", reply_markup=await admin_command())
    await state.clear()


@router.callback_query(F.data == "change_ref")
async def change_ref_handler(callback: types.CallbackQuery):
    current_ref = await DataBase.get_ref()
    message_text = (
        f"<b>Текущая реферальная ссылка:</b> <code>{current_ref}</code>\n\n"
        f"Для изменения отправьте новую ссылку в формате:\n"
        f"<code>/set_ref новая_ссылка</code>"
    )
    await callback.message.answer(message_text, parse_mode="HTML")
    await callback.answer()

@router.message(lambda message: message.text.startswith('/set_ref'))
async def set_ref_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        new_ref = message.text.split()[1]
        await DataBase.edit_ref(new_ref)
        await message.answer(f"✅ Реферальная ссылка успешно изменена на: <code>{new_ref}</code>", parse_mode="HTML")
    except Exception as e:
        await message.answer("❌ Ошибка при изменении ссылки. Проверьте формат команды:\n/set_ref новая_ссылка")