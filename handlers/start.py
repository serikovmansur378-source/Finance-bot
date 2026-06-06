from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Здравствуйте, {message.from_user.first_name}! Это ваш финансовый трекер.\n"
                         f"Это команды для вашего бота.\n"
                         f"/start - Для повторного отправление данного сообщения и начало общение, а так же\n"
                         f"может служить обновлением чата.\n"
                         f"/gave - это то, КТО ВАМ должен.\n"
                         f"/took - это КОМУ должны ВЫ.\n"
                         f"/debts - для просмотра всех ваших долгов\n"
                         f"/history - для просмотра истории доходов\расходов\n"
                         f"/reset [ОСТОРОЖНО] - Стирает абсолютно все ваши долги\расходы и т.д.\n")

