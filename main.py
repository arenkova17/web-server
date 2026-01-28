from fastapi import FastAPI
import uvicorn
from fastapi.responses import HTMLResponse
from database import get_all_klients, get_contract_id
from fastapi import HTTPException

#главная страница с таблицей
app = FastAPI()
@app.get("/", response_class=HTMLResponse)
def home():
    contracts = get_all_klients()  # получаем данные из database и присваиваем результат переменной
    #добавляем заголовок и название вкладки
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
    </style></head>
    <body>
        <h1 class="h1">Список договоров подлежащих публикации в ЕИС</h1>
        <table border="1" style="border-collapse: collapse; width: 100%;">
    """
    if contracts:  #если список получен
        html += "<tr style = 'background-color: #f2f2f2'>" #1 строка - заголовки. цвет - серый
        for key in contracts[0].keys():  #цикл прохода по первой строчке таблицы - заголовкам
            html += f"<th style='padding: 10px; border: 1px solid;'>{key}</th>" #оформление текста заголовков столбцов
        html += "</tr>"
        for contract in contracts:   #проход по строчкам договоров
            contract_id = contract['id']   #присваиваем id переменной
            html += f"<tr onclick='showContract({contract_id})'>"  #делаем строчку кликабельной
            for value in contract.values():  #проход по значениям одной строчки договора + оформление
                html += f"<td style='padding: 5px; border: 1px solid #ddd;'>{value}</td>"
            html += "</tr>"
    html += """</table>
    <script>
        function showContract(id) {
        window.location.href = '/contract/' + id;
    }
    </script>
    </body>
    </html> """
    return html

#функция для показа информации клиента
@app.get("/contract/{contract_id}", response_class=HTMLResponse)
def contract_page(contract_id: int):
    #присваивание результата функции в переменную
    contract = get_contract_id(contract_id)
    if not contract:
        return "<h1>Договор не найден</h1>"
    #оформление страницы договора
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
        text-decoration: none
        }}
    .h1 {{
        background: #e4f0fb; /* Цвет фона под заголовком */
        color: #0952a0; /* Цвет текста */
        padding: 8px; /* Поля вокруг текста */
    }}
    </style>
    </head>
    <body>
        <h1 class="h1">Информация по договору {contract_id}</h1>
        <p><strong>Дата договора:</strong> {contract.get('Дата начала', 'Нет данных')}</p>    
        <p><strong>Сумма договора:</strong> {contract.get('Сумма договора', 'Нет данных')} рублей</p>
        <p><strong>Предмет договора:</strong> {contract.get('Предмет договора', 'Нет данных')}</p>
        <p style="position: fixed; bottom: 20px; left: 20px;">
        <a href="/" class="button-back"> Назад к списку</a>
        </p>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000)

