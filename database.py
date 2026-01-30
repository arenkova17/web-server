import pyodbc
# подключение к бд
driver = '{ODBC Driver 17 for SQL Server}'
server = 'gazprosql'
database = 'tmp_dog'
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes'

#функция взятия столбцов из таблицы
def get_all_klients():
    try:
        #подключение к базе
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("select top 100 id, dn as 'Дата начала', summa as 'Сумма договора', predmet as 'Предмет договора' from dog")
        # Преобразуем в словари
        columns = [column[0] for column in cursor.description]   #извлекает заголовки столбцов
        result = []   #создаем список для хранения данных
        #проход по каждой строчке таблицы, запись в result в формате {'ID договора': 57, 'Дата начала': '2023-01-01', ...}
        for row in cursor.fetchall():  #fetchall - вся таблица, fetchone - первая запись
            row_dict = dict(zip(columns, row))
            result.append(row_dict)
        #закрытие соединения
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(f'Error: {e}')
        return []

#функция для добычи одного договора по id, нужна для окошка с инфой клиента
def get_contract_id(contract_id: int, ):
    try:
        #подключение к базе
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("select id, dn as 'Дата начала', summa as 'Сумма договора', predmet as 'Предмет договора' from dog where id = ?", contract_id) #ищем договор по id
        #получение названия колонок
        columns = [column[0] for column in cursor.description]
        #получение строки
        row = cursor.fetchone()
        #закрытие соединения
        cursor.close()
        connection.close()
        #если строка получена, возвращаем её в виде {'id': 57, 'Дата начала': '2023-01-01', ...}
        if row:
            return dict(zip(columns, row))
        else: return None

    except Exception as e:
        print(f'Error: {e}')
        return None

#функция обновления данных в базе
def update_contract(contract_id: int, dn: str, summa: float, predmet: str):
    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE dog 
            SET dn = ?, summa = ?, predmet = ?
            WHERE id = ?
        """, dn, summa, predmet, contract_id)

        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f'Update error: {e}')
        return False

