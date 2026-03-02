import pyodbc
import os
# подключение к бд
driver = '{ODBC Driver 17 for SQL Server}'
server = 'gazprosql'
database = 'tmp_dog'
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes'

#функция вывода таблицы почастично ( первые 4000 клиентов. вторые 4000 клиентов и тд)
def get_clients_page(page: int = 1, page_size: int = 4000):
    try:
        connection = pyodbc.connect(connection_string)
        if not connection:
            return []
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
        connection = pyodbc.connect(connection_string)
        if not connection:
            return []
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
                dk as 'Дата конца',
                klint.name as 'Наименование',
                klint.inn as 'ИНН',
                klint.rassh as 'Расч.счет',
                klint.bik as 'БИК',
                klint.KPP as 'КПП',
                klint.tel as 'Телефон/факс',
                dog.konk as 'Конкурс',
                
                dog.sposobzak as 'Способ закупки',
                dog.VIdZAK as 'Вид закупки',
                dog.numzak as 'Номер КЗ',
                dog.predlog as 'Формат закупки',
                dog.dat_docosznak as 'Дата основной закупки',
                dog.num_docosnzak as 'Номер основной закупки',
                dog.smsp as 'СМСП',
                dog.OSTNEKONZAK as 'Код основания',
                dog.okpd2 as 'ОКПД2',
                dog.subectzak as 'Субъектзак',
                
                dog_okz.num_z  as '№ закупки ЕИС', 
                dog_okz.num_z_el as '№ закупю на эл.пл.',
                dog_okz.pr_z as 'Прямая закупка',
                dog_okz.pr_z_osn as 'Основание',
                dog_okz.gpz as 'ГПЗ',
                dog_okz.UID_dog_ as 'UID',
                dog_okz.ppz as 'ППЗ',
                
                dog.prol as 'Пролонгация',
                dog.beznds as 'Без НДС',
                klint.asbu as 'Код ОБД НСИ',
                dog.opl as 'Оплачено',
                dog.eis as 'Публикация в ЕИС',
                dog_status.name_st as 'СТАТУС',
                dog.d_end as 'Дата заверш. договора'
            from dog 
            left join klint on dog.klient = klint.id
            left join dog_okz on dog.id = dog_okz.id_dog
            inner join dog_status on dog.statusD  = dog_status.id_status
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

#возвращение всех всех клиентов (нужно для просчета количества выводимых клиентов)
def get_total_count():
    """Возвращает общее количество договоров в таблице"""
    try:
        connection = pyodbc.connect(connection_string)
        if not connection:
            return []
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM dog")   #подсчет количества строк в таблице
        count = cursor.fetchone()[0]   #выводит первой строк - цифры количества строк

        cursor.close()
        connection.close()
        return count

    except Exception as e:
        print(f'Error in get_total_count: {e}')
        return 0

#обновление полей и чекбоксов
def update_par(contract_id: int, konk: int, prol: int, beznds: int, opl: int, eis: int, statusD: int, d_end: str, sposobzak: str, VIdZAK: int, numzak: str, predlog: int, dat_docosznak: str, num_docosnzak: int, smsp: int, OSTNEKONZAK: int, okpd2: int, subectzak: int, num_z: str, num_z_el: str, pr_z: int, pr_z_osn: str, gpz: str, uid: str, ppz: str):
    try:
        connection = pyodbc.connect(connection_string)
        if not connection:
            return []
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE dog 
            SET konk = ?,
            prol = ?,
            beznds = ?, 
            opl = ?, 
            eis = ?,
            statusD = ?,
            d_end = ?,
            
            sposobzak = ?,
            VIdZAK = ?,
            numzak = ?,
            predlog = ?,
            dat_docosznak = ?,
            num_docosnzak = ?,
            smsp = ?,
            OSTNEKONZAK = ?,
            okpd2 = ?,
            subectzak = ?
            WHERE id = ?
        """, konk, prol, beznds, opl, eis, statusD, d_end, sposobzak, VIdZAK, numzak, predlog, dat_docosznak, num_docosnzak, smsp, OSTNEKONZAK, okpd2, subectzak,  contract_id)

        cursor.execute("""
            UPDATE dog_okz 
            SET num_z = ?,
                num_z_el = ?,
                UID_dog_ = ?,
                pr_z = ?,
                pr_z_osn = ?,
                gpz = ?,
                ppz = ?
            WHERE id_dog = ?
        """, num_z, num_z_el, uid, pr_z, pr_z_osn, gpz, ppz, contract_id)

        connection.commit()
        cursor.close()
        connection.close()
        return True

    except Exception as e:
        print(f'Update error: {e}')
        return False

#функция поиска 1 или несколько договоров после нажатия кнопки найти на диалоговом окне
def search_dog(numberdog: str = "", numberkontr: str = ""):
    try:
        connection = pyodbc.connect(connection_string)
        if not connection:
            return []
        cursor = connection.cursor()

        if numberdog and numberkontr:
            cursor.execute("""
                SELECT 
                    dog.id as 'ID договора',
                    dbo.dog_fGetNum(dog.id) as 'Номер договора',
                    dog.n4 as '№ контрагента',
                    dog.dd as 'Дата договора',
                    klint.name as 'Контрагент', 
                    dog.predmet as 'Предмет договора'
                FROM dog
                LEFT JOIN klint ON dog.klient = klint.id
                WHERE dbo.dog_fGetNum(dog.id) = ? 
                  AND dog.n4 LIKE ?
                ORDER BY dog.id
            """, numberdog, f'%{numberkontr}%')

        elif numberdog:
            cursor.execute("""
            SELECT 
                    dog.id as 'ID договора',
                    dbo.dog_fGetNum(dog.id) as 'Номер договора',
                    dog.n4 as '№ контрагента',
                    dog.dd as 'Дата договора',
                    klint.name as 'Контрагент', 
                    dog.predmet as 'Предмет договора'
                FROM dog
                LEFT JOIN klint ON dog.klient = klint.id
                WHERE dbo.dog_fGetNum(dog.id) = ?
                ORDER BY dog.id
            """, numberdog)

        elif numberkontr:
            cursor.execute("""
            SELECT 
                    dog.id as 'ID договора',
                    dbo.dog_fGetNum(dog.id) as 'Номер договора',
                    dog.n4 as '№ контрагента',
                    dog.dd as 'Дата договора',
                    klint.name as 'Контрагент', 
                    dog.predmet as 'Предмет договора'
                FROM dog
                LEFT JOIN klint ON dog.klient = klint.id
                WHERE n4 like ?
                ORDER BY dog.id
            """, f'%{numberkontr}%')

        else:
            # Ничего не указано
            cursor.close()
            connection.close()
            return []

        columns = [column[0] for column in cursor.description]
        result = []

        for row in cursor.fetchall():
            result.append(dict(zip(columns, row)))

        cursor.close()
        connection.close()
        return result

    except Exception as e:
        print(f'Search error: {e}')
        return []

#функция берёт процедуру и вытаскивает результат процедуры
def get_dog_payments(contract_id: int):
    try:
        connection = pyodbc.connect(connection_string)
        if not connection:
            return []
        cursor = connection.cursor()

        cursor.execute("EXEC dog_opl_proc ?", contract_id)

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        payments = []
        for row in rows:
            payment_dict = dict(zip(columns, row))
            payments.append(payment_dict)

        cursor.close()
        connection.close()
        return payments

    except Exception as e:
        print(f'Error getting payments: {e}')
        return []



