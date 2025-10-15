# database/init_triggers.py
from database.db import db

def create_triggers_and_functions():
    db.connect()

    # -------------------------
    # Триггер: запрещаем удалять пользователей
    # -------------------------
    db.execute_sql("DROP TRIGGER IF EXISTS before_user_delete;")
    db.execute_sql("""
    CREATE TRIGGER before_user_delete
    BEFORE DELETE ON User
    FOR EACH ROW
    BEGIN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Нельзя удалить пользователя';
    END;
    """)

    # -------------------------
    # Валидация email при вставке и обновлении
    # -------------------------
    db.execute_sql("DROP TRIGGER IF EXISTS validate_email_insert;")
    db.execute_sql("""
    CREATE TRIGGER validate_email_insert
    BEFORE INSERT ON User
    FOR EACH ROW
    BEGIN
        IF NEW.email IS NOT NULL AND NEW.email NOT REGEXP '^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Неверный формат email';
        END IF;
    END;
    """)

    db.execute_sql("DROP TRIGGER IF EXISTS validate_email_update;")
    db.execute_sql("""
    CREATE TRIGGER validate_email_update
    BEFORE UPDATE ON User
    FOR EACH ROW
    BEGIN
        IF NEW.email IS NOT NULL AND NEW.email NOT REGEXP '^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Неверный формат email';
        END IF;
    END;
    """)

    # -------------------------
    # Валидация телефона при вставке и обновлении
    # -------------------------
    db.execute_sql("DROP TRIGGER IF EXISTS validate_phone_insert;")
    db.execute_sql("""
    CREATE TRIGGER validate_phone_insert
    BEFORE INSERT ON User
    FOR EACH ROW
    BEGIN
        IF NEW.phone IS NOT NULL AND NEW.phone NOT REGEXP '^\\+?\\d{10,15}$' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Неверный формат телефона';
        END IF;
    END;
    """)

    db.execute_sql("DROP TRIGGER IF EXISTS validate_phone_update;")
    db.execute_sql("""
    CREATE TRIGGER validate_phone_update
    BEFORE UPDATE ON User
    FOR EACH ROW
    BEGIN
        IF NEW.phone IS NOT NULL AND NEW.phone NOT REGEXP '^\\+?\\d{10,15}$' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Неверный формат телефона';
        END IF;
    END;
    """)

    # -------------------------
    # Автоматическое логирование действий при изменении заказов
    # -------------------------
    db.execute_sql("DROP TRIGGER IF EXISTS log_deal_update;")
    db.execute_sql("""
    CREATE TRIGGER log_deal_update
    AFTER UPDATE ON Deal
    FOR EACH ROW
    BEGIN
        INSERT INTO ActivityLog(user_id, action, created_at, assigned_to_id)
        VALUES (NEW.assigned_to_id, CONCAT('Обновлен заказ ID: ', NEW.id), NOW(), NEW.assigned_to_id);
    END;
    """)

    # -------------------------
    # Автоматическое обновление статуса задач при удалении клиента
    # -------------------------
    db.execute_sql("DROP TRIGGER IF EXISTS cascade_task_status_on_client_delete;")
    db.execute_sql("""
    CREATE TRIGGER cascade_task_status_on_client_delete
    BEFORE DELETE ON Client
    FOR EACH ROW
    BEGIN
        UPDATE Task SET status='cancelled' WHERE client_id=OLD.id;
    END;
    """)

    # -------------------------
    # Функция: подсчет задач пользователя
    # -------------------------
    db.execute_sql("DROP FUNCTION IF EXISTS count_user_tasks;")
    db.execute_sql("""
    CREATE FUNCTION count_user_tasks(user_id BIGINT) RETURNS INT
    DETERMINISTIC
    BEGIN
        DECLARE task_count INT;
        SELECT COUNT(*) INTO task_count FROM Task WHERE assigned_to_id = user_id;
        RETURN task_count;
    END;
    """)

    # -------------------------
    # Функция: подсчет сделок пользователя
    # -------------------------
    db.execute_sql("DROP FUNCTION IF EXISTS count_user_deals;")
    db.execute_sql("""
    CREATE FUNCTION count_user_deals(user_id BIGINT) RETURNS INT
    DETERMINISTIC
    BEGIN
        DECLARE deal_count INT;
        SELECT COUNT(*) INTO deal_count FROM Deal WHERE assigned_to_id = user_id;
        RETURN deal_count;
    END;
    """)

    # -------------------------
    # Функция: получение количества клиентов менеджера
    # -------------------------
    db.execute_sql("DROP FUNCTION IF EXISTS count_manager_clients;")
    db.execute_sql("""
    CREATE FUNCTION count_manager_clients(manager_id BIGINT) RETURNS INT
    DETERMINISTIC
    BEGIN
        DECLARE client_count INT;
        SELECT COUNT(*) INTO client_count FROM Client WHERE manager_id = manager_id;
        RETURN client_count;
    END;
    """)

    db.close()
    print("Все триггеры и функции созданы успешно!")

if __name__ == "__main__":
    create_triggers_and_functions()
