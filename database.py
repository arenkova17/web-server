import pyodbc
# подключение к бд
driver = '{ODBC Driver 17 for SQL Server}'
server = 'gazprosql'
database = 'tmp_dog'
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes'

#функция вывода таблицы почастично ( первые 4000 клиентов. вторые 4000 клиентов и тд)
def get_clients_page(page: int = 1, page_size: int = 4000):
    try:
        connection = pyodbc.connect(connection_string) #подключение к серверу через pyodbc
        cursor = connection.cursor()   #курсор для выполнения sql запросов

        # Рассчитываем offset (колво строк которые будем пропускать)
        offset = (page - 1) * page_size   #(1-1)*4000=0 (1 стр. пропускаем 0 строк), (2-1)*4000=4000 (2стр. пропукаем 4000 строк) и тд

        cursor.execute(f"""
            SELECT 
                dog.id as 'ID договора', 
                dbo.dog_fGetNum(dog.id) as 'Номер договора',
                dog.n4 as '№ контрагента',
                dog.dd as 'Дата договора',
                klint.name as 'Контрагент', 
                dog.predmet as 'Предмет договора'
            FROM dog 
            left join klint on dog.klient = klint.id
            ORDER BY dog.id
            OFFSET {offset} ROWS
            FETCH NEXT {page_size} ROWS ONLY
        """)

        columns = [column[0] for column in cursor.description]   #получение названия заголовков
        result = []   #создание списка

        for row in cursor.fetchall():    #fetchall - берет все строки. fetchone - получение первой строки
            row_dict = dict(zip(columns, row))    #zip(columns, row) получает сначала строку с заголовками, потом строку с его значением и соединяет их, а dict преобразует каждую такую строку в словарь типа  {'ID договора': 8001, '№ контрагента': '123', 'Дата начала': '2023-01-01', ...},
            result.append(row_dict)    #заносит результат в список

        cursor.close()
        connection.close()   #закрывается соединение
        return result    #возвращается результат

    except Exception as e:      #вывод ошибки и пустого списка в случае краха
        print(f'Error in get_clients_page: {e}')
        return []

#функция для добычи одного договора по id, нужна для окошка с инфой клиента
def get_contract_id(contract_id: int):
    try:
        #подключение к базе
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("""
            select 
                dog.id as 'ID договора',
                dbo.dog_fGetNum(dog.id) as '№ договора',
                n4 as '№ контрагента',
                dn as 'Дата начала',
                summa as 'Сумма договора',
                predmet as 'Предмет договора',
                dr as 'Дата регистрации',
                dd as 'Дата договора',
                podr as 'Подразделение',
                dk as 'Дата конца'
            from dog 
            left join klint on dog.klient = klint.id
            where dog.id = ?
        """, contract_id)

        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()   #получение строки

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
def update_contract(contract_id: int, n4: str, dn: str, summa: float, predmet: str, dr: str):     #передача параметров для обновления
    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        cursor.execute("""     --получение значений для обновления и обновление
            UPDATE dog 
            SET n4 = ?, dn = ?, summa = ?, predmet = ?, dr = ?
            WHERE id = ?
        """, n4, dn, summa, predmet, contract_id, dr)

        connection.commit()    #команда сохранения результатом
        cursor.close()
        connection.close()
        return True

    except Exception as e:
        print(f'Update error: {e}')
        return False

#возвращение всех всех клиентов (нужно для просчета количества выводимых клиентов)
def get_total_count():
    """Возвращает общее количество договоров в таблице"""
    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM dog")   #подсчет количества строк в таблице
        count = cursor.fetchone()[0]   #выводит первой строк - цифры количества строк

        cursor.close()
        connection.close()
        return count

    except Exception as e:
        print(f'Error in get_total_count: {e}')
        return 0
