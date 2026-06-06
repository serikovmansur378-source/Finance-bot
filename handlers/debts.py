from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database.repositories import DebtRepository

router = Router()


@router.message(Command("gave"))
async def cmd_gave(message: Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("⚠️ Format: `/gave Name Sum` (For example: `/gave Иван 500`)", parse_mode="Markdown")
        return

    debtor_name = args[1]
    try:
        amount = float(args[2])
        user_id = message.from_user.id

        success = DebtRepository.add_debt(user_id, debtor_name, amount, is_given=True, is_active=True)

        if success:
            await message.answer(f"🤝 Recorded: {debtor_name} owes you {amount} тг.")
        else:
            await message.answer("❌ Error saving to DB.")
    except ValueError:
        await message.answer("❌ Sum must be a number!")


@router.message(Command("took"))
async def cmd_took(message: Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("⚠️ Format: `/took Name Sum` (For example: `/took Иван 1000`)", parse_mode="Markdown")
        return

    debtor_name = args[1]
    try:
        amount = float(args[2])
        user_id = message.from_user.id

        success = DebtRepository.add_debt(user_id, debtor_name, amount, is_given=False, is_active=True)

        if success:
            await message.answer(f"💸 Recorded: You owe {debtor_name} {amount} тг.")
        else:
            await message.answer("❌ Error saving to DB.")
    except ValueError:
        await message.answer("❌ Sum must be a number!")


@router.message(Command("debts"))
async def cmd_list_debts(message: Message):
    user_id = message.from_user.id
    debts = DebtRepository.get_user_debts(user_id)

    if not debts:
        await message.answer("📋 <b>Your debts:</b>\nYou have no active debts.", parse_mode="HTML")
        return

    i_gave = []
    i_took = []

    total_owed_to_me = 0.0
    total_i_owe = 0.0

    processed_names = set()

    for name, amount, is_given, due_date, given_date in debts:
        if name in processed_names:
            continue

        total_balance = DebtRepository.get_total_debt_balance(user_id, name)

        if total_balance <= 0:
            continue

        created_str = given_date.strftime("%d.%m.%Y")
        due_str = f" (до {due_date})" if due_date else ""

        if is_given:
            i_gave.append(f"🟢 {name} Должны вам: {total_balance:.2f} тг. [Записано в {created_str}]{due_str}")

            total_owed_to_me += total_balance
        else:
            i_took.append(f"🔴 Вы должны {name}: {total_balance:.2f} тг. [Записано в {created_str}]{due_str}")

            total_i_owe += total_balance

        processed_names.add(name)

    text_lines = ["📋 <b>Долги:</b>\n"]

    if i_gave:
        text_lines.extend(i_gave)
        text_lines.append(f"<b>В сумме вам должны: {total_owed_to_me:.2f} тг.</b>\n")

    if i_took:
        text_lines.extend(i_took)
        text_lines.append(f"<b>В сумме вы должны: {total_i_owe:.2f} тг.</b>")

    if len(text_lines) <= 1:
        await message.answer("📋 <b>Your debts:</b>\nYou have no active debts.", parse_mode="HTML")
        return

    full_text = "\n".join(text_lines)
    await message.answer(full_text, parse_mode="HTML")


@router.message(Command("return"))
async def cmd_return_debt(message: Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("⚠️ Format: `/return Name Sum` (For example: `/return Иван 200`)", parse_mode="Markdown")
        return

    debtor_name = args[1]
    try:
        amount_returned = float(args[2])
        user_id = message.from_user.id

        current_balance = DebtRepository.get_total_debt_balance(user_id, debtor_name)
        if current_balance == 0:
            await message.answer(f"❌ У тебя нет активных долгов с именем {debtor_name}.")
            return


        debts = DebtRepository.get_user_debts(user_id)
        is_given_type = True
        for name, _, is_given, _, _ in debts:
            if name == debtor_name:
                is_given_type = is_given
                break


        success = DebtRepository.add_debt(user_id, debtor_name, -amount_returned, is_given=is_given_type,
                                          is_active=True)

        if not success:
            await message.answer("❌ Ошибка при записи возврата в базу.")
            return

        new_balance = DebtRepository.get_total_debt_balance(user_id, debtor_name)

        from database.repositories import TransactionRepository
        TransactionRepository.add_transaction(user_id, amount_returned, f"Возврат долга: {debtor_name}")

        if new_balance <= 0:
            DebtRepository.archive_debt_history(user_id, debtor_name)
            await message.answer(f"🎉 Долг с {debtor_name} полностью закрыт в 0! Все записи сохранены в архиве истории.")
        else:
            await message.answer(
                f"📉 Записан возврат от {debtor_name} на сумму {amount_returned} тг.\n"
                f"Остаток долга: <b>{new_balance:.2f} тг.</b>",
                parse_mode="HTML"
            )

    except ValueError:
        await message.answer("❌ Сумма должна быть числом!")