from database.db import db


def create_triggers_and_functions():
    db.connect()

    # ===============================
    # Триггер: при удалении пользователя, проверить есть ли клиенты
    # ===============================
    db.execute_sql("""
    CREATE TRIGGER before_user_delete
    BEFORE DELETE ON User
    FOR EACH ROW
    BEGIN
        DECLARE client_count INT;
        SELECT COUNT(*) INTO client_count FROM Client WHERE created_by = OLD.id;
        IF client_count > 0 THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Невозможно удалить пользователя с клиентами';
        END IF;
    END;
    """)

    # ===============================
    # Триггер: при обновлении статуса задачи автоматически логировать
    # ===============================
    db.execute_sql("""
    CREATE TRIGGER after_task_update
    AFTER UPDATE ON Task
    FOR EACH ROW
    BEGIN
        IF OLD.status != NEW.status THEN
            INSERT INTO ActivityLog (user_id, action, created_at)
            VALUES (NEW.assigned_to, CONCAT('Статус задачи изменен с ', OLD.status, ' на ', NEW.status), NOW());
        END IF;
    END;
    """)

    # ===============================
    # Триггер: при вставке нового заказа логируем событие
    # ===============================
    db.execute_sql("""
    CREATE TRIGGER after_deal_insert
    AFTER INSERT ON Deal
    FOR EACH ROW
    BEGIN
        INSERT INTO ActivityLog (user_id, action, created_at)
        VALUES (NEW.assigned_to, CONCAT('Создан новый заказ: ', NEW.title), NOW());
    END;
    """)

    # ===============================
    # Функция: подсчет активных задач по пользователю
    # ===============================
    db.execute_sql("""
    DROP FUNCTION IF EXISTS get_active_tasks;
    """)
    db.execute_sql("""
    CREATE FUNCTION get_active_tasks(user_id BIGINT) RETURNS INT
    DETERMINISTIC
    BEGIN
        DECLARE task_count INT;
        SELECT COUNT(*) INTO task_count FROM Task 
        WHERE assigned_to = user_id AND status != 'done';
        RETURN task_count;
    END;
    """)

    # ===============================
    # Функция: подсчет открытых заказов по менеджеру
    # ===============================
    db.execute_sql("""
    DROP FUNCTION IF EXISTS get_open_deals;
    """)
    db.execute_sql("""
    CREATE FUNCTION get_open_deals(manager_id BIGINT) RETURNS INT
    DETERMINISTIC
    BEGIN
        DECLARE deal_count INT;
        SELECT COUNT(*) INTO deal_count FROM Deal
        WHERE assigned_to = manager_id AND status = 'open';
        RETURN deal_count;
    END;
    """)

    # ===============================
    # Функция: поиск клиента по имени, телефону или email
    # ===============================
    db.execute_sql("""
    DROP FUNCTION IF EXISTS search_client;
    """)
    db.execute_sql("""
    CREATE FUNCTION search_client(search_text VARCHAR(255)) RETURNS INT
    DETERMINISTIC
    BEGIN
        DECLARE client_id INT;
        SELECT id INTO client_id FROM Client
        WHERE name LIKE CONCAT('%', search_text, '%')
           OR phone LIKE CONCAT('%', search_text, '%')
           OR email LIKE CONCAT('%', search_text, '%')
        LIMIT 1;
        RETURN client_id;
    END;
    """)

    db.close()
    print("Триггеры и функции созданы успешно!")
