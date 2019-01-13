### Парсинг hh.ru на стэк скилов для разработчиков  

установить зависимости  
```bash
pip install -r requirements.txt
```

изменить конфиг
```ini
[default]
; cann't be changed
tmp_link = https://hh.ru/search/vacancy?area=1&clusters=true&enable_snippets=true&only_with_salary={ows}&salary={salary}&text={position}&page={page_num}
vacancy_volume_regex = data-totalVacancies="(\d+)"
vacancy_link_regex = https:\/\/hh.ru\/vacancy\/\d+\?query={position}
pages_num_regex = data-page="(\d+)"
vac_desc_div_class = g-user-content

; can be changed
; позиция
position = python engineer 
; ЗП в рублях
salary = 200000
; позволить учавствовать в выборке вакансиям без указанной ЗП
only_with_salary = false
; максимальная выборка вакансий
max_vacancies = 200
; максимальное количесвто скилов в выводе в косноль (в файл сохранится все)
max_skills = 30

[path]
results = results
stop_words = ignore_words.txt
```

запустить  
```bash
python3 main.py
```

проверить результаты в консоли или в директории `results/`