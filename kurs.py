import json
from requests import get

data = get('https://open.er-api.com/v6/latest/CNY')
if data.status_code != 200:
    pass
else:
    data_j = json.loads(data.text)
    with open('/var/www/u2302856/data/www/himerastore.ru/kurs.txt', 'w') as f:
        f.write(str(data_j['rates']['RUB']))