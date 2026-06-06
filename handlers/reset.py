from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database.repositories import TransactionRepository

router = Router()


@router.message(Command("reset"))
async def cmd_reset(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💥 Да, удалить всё", callback_data="confirm_reset"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_reset")
            ]
        ]
    )

    await message.answer(
        "⚠️ <b>ВНИМАНИЕ!</b> Ты собираешься полностью удалить всю историю своих доходов, расходов и долгов.\n"
        "Это действие невозможно отменить. Ты абсолютно уверен?",
        reply_markup=keyboard,
        parse_mode="HTML"
    )



@router.callback_query(F.data == "confirm_reset")
async def process_confirm_reset(callback: CallbackQuery):
    user_id = callback.from_user.id


    success = TransactionRepository.reset_user_data(user_id)

    if success:

        await callback.message.edit_text("🔥 Всё успешно удалено")
    else:
        await callback.message.edit_text("❌ Произошла ошибка на сервере при удалении данных.")


    await callback.answer()



@router.callback_query(F.data == "cancel_reset")
async def process_cancel_reset(callback: CallbackQuery):
    await callback.message.edit_text(" Сброс отменен.")
    await callback.answer()