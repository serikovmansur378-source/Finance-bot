from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database.repositories import TransactionRepository

router = Router()

@router.message(Command("history"))
async def cmd_history(message: Message):
    user_id = message.from_user.id
    expenses = TransactionRepository.get_user_expenses(user_id)

    if not expenses:
        await message.answer("У вас ещё нет записей о финансах")
        return

    text = "📊 **История твоих операций:**\n\n"

    for amount, category, timestamp in expenses:
        date_str = timestamp.strftime("%d.%m.%Y. %H.%M")

        if amount < 0:
            text += f"🔴 {amount} тг - {category} | _{date_str}_\n"
        else:
            text += f"🟢 +{amount} тг - {category} | _{date_str}_\n"

    await message.answer(text, parse_mode="Markdown")

@router.message(F.text.regexp(r'^[\d+=]'))
async def handle_expense(message: Message):
    text = message.text.strip()

    try:

        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            return
        amount_str, category = parts
        amount = float(amount_str)
        user_id = message.from_user.id

        success = TransactionRepository.add_transaction(user_id, amount, category)

        if success:
            if amount < 0:
                await message.answer(f"📉 Записано: {amount} тг. в категорию '{category}'")
            else:
                await message.answer(f"📈 Записано: +{amount} тг. в категорию '{category}'")
        else:
            await message.answer("❌ Ошибка при сохранении в базу данных.")

    except ValueError:
        pass