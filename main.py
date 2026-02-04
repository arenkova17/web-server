from fastapi import FastAPI
import uvicorn
from fastapi.responses import HTMLResponse
from database import get_clients_page, get_total_count, get_contract_id, update_contract
from fastapi import HTTPException
from fastapi import Form

# главная страница с таблицей
app = FastAPI()


# функция главного экрана с пагинацией
@app.get("/", response_class=HTMLResponse)
def home(page: int = 1, page_size: int = 4000):
    contracts = get_clients_page(page, page_size)  # занесение списка из строк которые будем выводить
    total_count = get_total_count()  # занесение общего числа строк

    # расссчитывает сколько всего должно быть страниц на всё количество с округлением вверх
    total_pages = (total_count + page_size - 1) // page_size
    html = """  
    <html>
    <head><title>Договора в ЕИС</title>  
    <style>
    .h1 {
        background: #e4f0fb; /* Цвет фона под заголовком */
        color: #0952a0; /* Цвет текста */
        padding: 8px; /* Поля вокруг текста */
    }
    .column-names {
        color: #0952a0; /* Цвет текста */
    }
    tr:hover {
        background-color: #f5f5f5; /* цвет при наведении */
        cursor: pointer;           /* курсор в виде руки */
    }
        .pagination {      /* стиль для одной иконки страницы */
        margin: 20px 0;
        text-align: center;
    }  
    .pagination a {        /* стиль для всех иконок страниц */
        display: inline-block;
        padding: 5px 10px;
        margin: 0 2px;
        border: 1px solid #ddd;
        text-decoration: none;
    }
    .pagination a.active {     /* стиль для активной страницы, которая нажата */
        background: #032c57;
        color: white;
    }
    </style></head>
    <body>
        <h1 class="h1">Список договоров подлежащих публикации в ЕИС</h1>
        <table border="1" style="border-collapse: collapse; width: 100%;">
    """
    if contracts:  # если список получен
        html += "<tr style = 'background-color: #f2f2f2'>"  # 1 строка - заголовки. цвет - серый
        for key in contracts[0].keys():  # цикл прохода по первой строчке таблицы - заголовкам
            html += f"<th style='padding: 10px; border: 1px solid;'>{key}</th>"  # оформление текста заголовков столбцов
        html += "</tr>"
        for contract in contracts:  # проход по строчкам договоров
            contract_id = contract['ID договора']  # присваиваем id переменной
            html += f"<tr onclick='showContract({contract_id}, {page})'>"  # делаем строчку кликабельной
            for value in contract.values():  # проход по значениям одной строчки договора + оформление
                html += f"<td style='padding: 5px; border: 1px solid #ddd;'>{value}</td>"
            html += "</tr>"
    html += f"""</table>   
    <script>         /* функция для перехода на страницу договора */
        function showContract(id, page) {{        /* передача номера договора и номер страницы */
            window.location.href = '/contract/' + id + '?from_page=' + page;        /* меняет url на адрес с договором и перенаправляет на страницу */
        }} 
    </script>

    <div class="pagination">
    """

    for i in range(1,
                   total_pages + 1):  # рассчитывает сколько кнопок пагинации надо создать. если total_pages = 4, то кнопок 4
        active_class = "active" if i == page else ""  # определяет активную кнопку. если i равняется номеру открытой страницы, то применяется к ней стиль active_class
        html += f'<a href="/?page={i}&page_size={page_size}" class="{active_class}">{i}</a>'  # создание самой кнопки страницы

    html += """
    </div>
    </body>
    </html>
    """
    return html


# функция для показа информации клиента
@app.get("/contract/{contract_id}", response_class=HTMLResponse)
def contract_page(contract_id: int, from_page: int = 1):
    # присваивание результата функции в переменную
    contract = get_contract_id(contract_id)
    if not contract:
        return "<h1>Договор не найден</h1>"
    # оформление страницы договора
    html = f"""
    <html>
    <head><title>Договор {contract_id}</title>
    <style>
    .button-back {{
        border: 3px solid #1073b7; /* Параметры рамки */
        background: #1073b7; /* Цвет фона */
        font-size: 18px; /* Размер текста */
        padding: 5px 20px; /* Поля вокруг текста */
        color: white;
        text-decoration: none;
        }}
    .h1 {{
        background: #e4f0fb; /* Цвет фона под заголовком */
        color: #0952a0; /* Цвет текста */
        padding: 8px; /* Поля вокруг текста */
    }}
    .button-edit {{
    border: 3px solid #1073b7; /* Параметры рамки */
        background: #1073b7; /* Цвет фона */
        font-size: 18px; /* Размер текста */
        padding: 5px 20px; /* Поля вокруг текста */
        color: white;
        text-decoration: none;
    }}
    </style>
    </head>
    <body>
        <h1 class="h1">Информация по договору {contract_id}</h1>
        <p><strong>№ договора:</strong> {contract.get('№ договора', 'Нет данных')}</p>
        <p><strong>№ контрагента:</strong> {contract.get('№ контрагента', 'Нет данных')}</p>
        <p><strong>Дата регистрации:</strong> {contract.get('Дата регистрации', 'Нет данных')}</p>
        <p><strong>Дата договора:</strong> {contract.get('Дата договора', 'Нет данных')}</p>
        <p><strong>Подразделение:</strong> {contract.get('Подразделение', 'Нет данных')}</p>
        <p><strong>Предмет договора:</strong> {contract.get('Предмет договора', 'Нет данных')}</p>
        <p><strong>Дата договора:</strong> {contract.get('Дата начала', 'Нет данных')}</p>   
        <p><strong>Дата конца:</strong> {contract.get('Дата конца', 'Нет данных')}</p> 
        <p><strong>Сумма договора:</strong> {contract.get('Сумма договора', 'Нет данных')} рублей</p>

        <p style="position: fixed; bottom: 20px; left: 20px;">
        <a href="/?page={from_page}" class="button-back"> Назад к списку</a>
        </p>
        <p style="position:fixed; bottom: 20px; right: 20px">
        <a href="/contract/{contract_id}/update" class="button-edit"> Изменить </a>
        </p>


    </body>
    </html>
    """
    return html


# функуция которая заполняет значения в изменении ( окно редактирования )
@app.get("/contract/{contract_id}/update", response_class=HTMLResponse)
def edit_contract_page(contract_id: int):
    contract = get_contract_id(contract_id)
    if not contract:
        return "<h1>Договор не найден</h1>"
    raw_date = str(contract.get('Дата начала', ''))  # точно в строку
    formatted_date = raw_date[:10] if raw_date else ''

    raw_date_dr = str(contract.get('Дата регистрации', ''))  # точно в строку
    formatted_date_dr = raw_date[:10] if raw_date else ''

    html = f"""
    <html>
    <head><title>Изменение данных</title>
    <style>
    .h1 {{
        background: #e4f0fb; /* Цвет фона под заголовком */
        color: #0952a0; /* Цвет текста */
        padding: 8px; /* Поля вокруг текста */
    }}
    .button-edit {{   /*сохранить*/
        border: 3px solid #1073b7; /* Параметры рамки */
        background: #1073b7; /* Цвет фона */
        font-size: 18px; /* Размер текста */
        padding: 5px 20px; /* Поля вокруг текста */
        color: white;
        text-decoration: none;
        }}
    .button-back {{    /*назад к просмотру*/
        border: 3px solid #1073b7; /* Параметры рамки */
        background: #1073b7; /* Цвет фона */
        font-size: 18px; /* Размер текста */
        padding: 5px 20px; /* Поля вокруг текста */
        color: white;
        text-decoration: none;
    }}
    </style>
    </head>
    <body>
    <h1 class="h1">Изменение данных договора {contract_id}</h1>
    <form action="/api/contract/{contract_id}/update" method="POST">
        <label><strong>№ контрагента:</strong></label>
            <input type="text" name="n4" value="{contract.get('№ контрагента', 0)}"><br><br>
        <label><strong>Дата договора:</strong></label>
            <input type="date" name="dn" value="{formatted_date}"><br><br>
        <label><strong>Сумма договора:</strong></label>
            <input type="number" name="summa" value="{contract.get('Сумма договора', 0)}"><br><br>
        <label><strong>Предмет договора:</strong></label>
            <input type="text" name="predmet" value="{contract.get('Предмет договора', '')}"><br><br>
        <label><strong>Дата регистрации:</strong></label>
            <input type="date" name="dr" value="{formatted_date_dr}"><br><br>
        <p style="position: fixed; bottom: 20px; right: 20px;">
        <a href="#" onclick="this.closest('form').submit(); return false;" class="button-edit">Сохранить</a>
    </form>

    <p style="position: fixed; bottom: 20px; left: 20px;">
    <a href="/contract/{contract_id}" class="button-back">Назад к просмотру</a></p>

    </body>
    </html>
    """
    return html


# функция обновления данных в базе
@app.post("/api/contract/{contract_id}/update")
def update_contract_api(
        contract_id: int,
        n4: str = Form(...),
        dn: str = Form(...),
        summa: float = Form(...),
        predmet: str = Form(...),
        dr: str = Form(...)):
    success = update_contract(contract_id, n4, dn, summa, predmet, dr)

    if success:
        # Возвращаем обратно на страницу договора
        return HTMLResponse(f"""
            <script>
                alert('Договор обновлён!');
                window.location.href = '/contract/{contract_id}';
            </script>
        """)
    else:
        raise HTTPException(500, "Ошибка при обновлении")


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
