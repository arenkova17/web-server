import pyodbc
# подключение к бд
driver = '{ODBC Driver 17 for SQL Server}'
server = 'gazprosql'
database = 'tmp_dog'
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes'

def get_clients_page(page: int = 1, page_size: int = 4000):
    """
    Получает одну страницу договоров
    page: номер страницы (начинается с 1)
    page_size: сколько строк на странице
    """
    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # Рассчитываем offset
        offset = (page - 1) * page_size

        cursor.execute(f"""
            SELECT 
                id as 'ID договора', 
                dn as 'Дата начала', 
                summa as 'Сумма договора', 
                predmet as 'Предмет договора'
            FROM dog 
            ORDER BY id
            OFFSET {offset} ROWS 
            FETCH NEXT {page_size} ROWS ONLY
        """)

        columns = [column[0] for column in cursor.description]
        result = []

        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            result.append(row_dict)

        cursor.close()
        connection.close()
        return result

    except Exception as e:
        print(f'Error in get_clients_page: {e}')
        return []

#функция для добычи одного договора по id, нужна для окошка с инфой клиента
def get_contract_id(contract_id: int, ):
    try:
        #подключение к базе
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("select id as 'ID договора', dn as 'Дата начала', summa as 'Сумма договора', predmet as 'Предмет договора' from dog where id = ?", contract_id) #ищем договор по id
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





def get_total_count():
    """Возвращает общее количество договоров в таблице"""
    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM dog")
        count = cursor.fetchone()[0]

        cursor.close()
        connection.close()
        return count

    except Exception as e:
        print(f'Error in get_total_count: {e}')
        return 0
