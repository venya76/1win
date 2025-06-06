from aiogram.utils.keyboard import InlineKeyboardBuilder

async def admin_command():
    ikb = InlineKeyboardBuilder()

    ikb.button(text="Рассылка📩", callback_data="mailing")
    ikb.button(text="Смена реферальной ссылки🔗", callback_data="change_ref")
    ikb.button(text="Статистика📊", callback_data="stat")
    ikb.adjust(1, 1)
    return ikb.as_markup()

async def get_mailing_type_keyboard():
    ikb = InlineKeyboardBuilder()
    
    ikb.button(text="Всем пользователям 👥(всем тиграм)", callback_data="mailing_all")
    ikb.button(text="С депозитом 💰(тигры львы нахуй)", callback_data="mailing_deposit")
    ikb.button(text="С регой, без депа💖(пидоры в 9999 степени) ", callback_data="mailing_new")
    ikb.button(text="Ни реги ни депа, пидоры одним словом 🆘 (черти нахуй)", callback_data="mailing_unverified_nodep")
    ikb.button(text="Отмена", callback_data="decline_mailing")
    
    ikb.adjust(1)
    return ikb.as_markup()