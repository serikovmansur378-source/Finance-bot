from database.connection import get_db_connection

class TransactionRepository:

    @staticmethod
    def add_transaction(user_id: int, amount: float, category: str):
        conn = get_db_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cursor:
                query = """
                INSERT INTO transactions (user_id, amount, category)
                VALUES (%s, %s, %s);
                """
                cursor.execute(query, (user_id, amount, category))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка сохранений транзакции: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def reset_user_data(user_id: int) -> bool:
        conn = get_db_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cursor:

                cursor.execute("DELETE FROM transactions WHERE user_id = %s;", (user_id,))

                cursor.execute("DELETE FROM debts WHERE user_id = %s;", (user_id,))

                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка при удалении данных пользователя {user_id}: {e}")
            return False
        finally:
            conn.close()



    @staticmethod
    def get_user_expenses(user_id: int):
        conn = get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cursor:

                query = """
                SELECT amount, category, timestamp 
                FROM transactions
                WHERE user_id = %s 
                ORDER BY timestamp DESC;
                """
                cursor.execute(query, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка взятия Транзакции: {e}")
            return []
        finally:
            conn.close()


class DebtRepository:

    @staticmethod
    def reduce_debt(user_id: int, debtor_name: str, amount_to_reduce: float) -> dict:

        conn = get_db_connection()
        if not conn:
            return {"status": "error", "message": "Нет подключения к БД"}

        try:
            with conn.cursor() as cursor:

                query_select = """
                    SELECT id, amount, is_given FROM debts 
                    WHERE user_id = %s AND debtor_name = %s
                    ORDER BY given_date DESC LIMIT 1;
                    """
                cursor.execute(query_select, (user_id, debtor_name))
                debt = cursor.fetchone()

                if not debt:
                    return {"status": "not_found", "message": f"Долг с именем {debtor_name} не найден."}

                debt_id, current_amount, is_given = debt
                new_amount = float(current_amount) - amount_to_reduce

                if new_amount <= 0:

                    cursor.execute("DELETE FROM debts WHERE id = %s;", (debt_id,))
                    conn.commit()
                    return {"status": "closed", "is_given": is_given, "remaining": 0}
                else:

                    cursor.execute("UPDATE debts SET amount = %s WHERE id = %s;", (new_amount, debt_id))
                    conn.commit()
                    return {"status": "reduced", "is_given": is_given, "remaining": new_amount}

        except Exception as e:
            print(f"Ошибка при погашении долга: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            conn.close()



    @staticmethod
    def add_debt(user_id: int, debtor_name: str, amount: float, is_given: bool, is_active: bool = True):
        conn = get_db_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO debts (user_id, debtor_name, amount, is_given, is_active) 
                    VALUES (%s, %s, %s, %s, %s);
                    """
                cursor.execute(query, (user_id, debtor_name, amount, is_given, is_active))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка сохранения долга: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_user_debts(user_id: int):
        conn = get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT debtor_name, amount, is_given, due_date, given_date 
                    FROM debts 
                    WHERE user_id = %s AND is_active = TRUE
                    ORDER BY given_date DESC;
                    """
                cursor.execute(query, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения активных долгов: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_total_debt_balance(user_id: int, debtor_name: str) -> float:
        conn = get_db_connection()
        if not conn:
            return 0.0
        try:
            with conn.cursor() as cursor:
                query = "SELECT SUM(amount) FROM debts WHERE user_id = %s AND debtor_name = %s;"
                cursor.execute(query, (user_id, debtor_name))
                res = cursor.fetchone()[0]
                return float(res) if res else 0.0
        except Exception as e:
            print(f"Ошибка подсчета баланса долга: {e}")
            return 0.0
        finally:
            conn.close()

    @staticmethod
    def archive_debt_history(user_id: int, debtor_name: str):
        conn = get_db_connection()
        if not conn:
            return
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE debts SET is_active = FALSE WHERE user_id = %s AND debtor_name = %s;",
                    (user_id, debtor_name)
                )
                conn.commit()
        except Exception as e:
            print(f"Ошибка архивации: {e}")
        finally:
            conn.close()

