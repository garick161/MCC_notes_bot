# Телеграмм бот для отправки замечаний машинистами электропоездов на инфратруктуре Московского Центрального Кольца
#![mcc](https://github.com/garick161/MCC_notes_bot/assets/114688542/fcbfd1cb-0bbc-4594-b718-c9f97ec1effc)

Бот предназначен для упрощения передачи в основном рутинных замечаний, не влияющих на безопасность движения. В случае угрозе безопасности движения замечания передавать только по радиосвязи.
Использование бота позволит снизить нагрузку на ДСП, ДНЦ и конечно на машинистов, что особенно важно в условиях высокоинтенсивного движения как на МЦК. Это позволит меньше отвлекаться и сосредоточится на выполнении своих непосредственных обязанностей.
Так же нет необходимости заполнять книгу замечаний после смены. В электронном виде будет все и доступно в любой момент по запросу.
Нужно печатный(классический вид) - сделал запрос одной командой - распечатал - поставили росписи - готово!

# Как это работает?

1) <em><u>Передача замечаний</u></em>
- Машинист надиктовывает замечание в виде голосового сообщения
- Бот использует языковую модель на основе нейронной сети и распознает текст, выделяет нужные паттерны
- Формирует предварительный отчет с распознанной информацией. При желании можно отредактировать или отправить замечание заново
- При наличии связи с АРМ(система регистрации поездок) никакой дополнительной информации вводить не нужно. Все данные о поездке подтягиваются автоматически
- При отсутствии связи с АРМ - необходимо ввести дополнительные данные. Бот подскажет какие
- После заполнения замечание записывается в базу данных. И далее доступны в виде книги замечаний по запросу

2) <em><u>Получение замечаний ДСП/ДНЦ</u></em>

Даже если вы не выбрали станцию программа автоматически поймет какому ДСП/ДНЦ нужно отправить сообщение. Уведомление им прийдет в любом удобном виде(телеграмм, почта...). Так же у них будет доступ к базе, чтобы обработать замечание. Опять же нет никакой необходимости руками вносить информацию, все уже есть в электронном варианте.

3) <em><u>Получение отчетов и статистик</u></em>

Набрав команду /reports или кликнув на нее вы можете получить доступ к формированию отчетов из книги замечаний, агрегации и графиков статистики.

# Составные части проекта

1. Сам телегамм бот написан с использованием бибилиотеки `pyTelegramBotAPI`
2. Для распознавания и транскипции текста использовалась предобученная мультиязычная модель `whisper-small` от OpenAI
3. Выделение нужных паттернов из текста. Использовались регуляные выражения
4. Считывание и валидация дополнительных данных от пользователя
5. Запись информации в базы данных. Регистрация переданных замечаний в виде аудиозаписей. Логирование каждой комунникации с пользователем
6. Реализация возможности полученения отчетов, агрегации, графиков

# Описание структуры проекта
`scripts`

Cодержит только питоноские скрипты, необходимые для работы приложения

- `note_bot.py`	- Основной файл, в котором реализования вся логика работы бота
- `transformers_whisper.py`	- Распознавание и транскрипция текста
- `format_text.py` -	Выделение нужных паттернов из текста замечания
- `data_validation.py` -	Валидация данных, передаваемых пользователем
- `db_connection.py`	- Файл для работы с базами данных
- `reports.py`	- Файл для формирования отчетов и статистик

`volumes/data_bases`

- `notes.sql`	- Основная база данных(чистовая) для хранения информации о переданном замечании согласно регламенту железных дорог. На основании ее формируется книга замечаний и необходимые отчеты
- `history_db.sql` - База для внутренних нужд. Для мониторинга работы бота и качества распознавания текста

`volumes/voices`

Содержит голосовые записи переданных замечаний, которые были успешно записаны в читовую базу `notes.sql`. Название аудиофайлов соответвует номеру `id` в базе данных. Так что не составит труда найти для конктретного замечания запись или наоборот

`volumes/history_log_voices`

Содержит голосовые записи всех переданных замечаний, в том числе и неудачных. Используются для мониторинга работы бота, качество распознавания замечаний. Можно понять какие трудности возникают при передаче замечаний. Название аудиофайлов соответвуют формату: "hour_minutes-day_month_year.ogg". По этому времени можно найти нужные логи и наоборот

`volumes/history_log`

Содержит все логи для каждой коммуникации с пользователем. Записывает все основные этапы взаимодейтвия с пользователем. По этой информации можно искать баги или моменты, в которые вызывают у пользвателей затруднения. Все ошибки, по причинам которых программа может упасть мы тоже увидим в логах

Содержит голосовые записи переданных замечаний, которые были успешно записаны в читовую базу `notes.sql`. Название аудиофайлов соответвует номеру `id` в базе данных. Так что не составит труда найти для конктретного замечания запись или наоборот

`addition_files`

Содержит содержит служебные информационные файлы для работы бота. Так же в этой папке содержатся файлы для отправки пользователю в случае затруднений. Например, схема расположения станций или пример записи голосового сообщения согласно регламенту переговоров

`temp_report_files`

Содержит временные файлы для отчетов

`root_dir`

Файлы в корневом каталоге

- `requirements.txt` - Список необходимых библиотек
- `Dockerfile` - Файл для сборки образа Docker
- `.dockerignore`	- Что не добавлять в образ
- `commands.sh`	- bash скрипт с командами для создания образа и поднятия контейнера

# Как запустить?
1) `Docker` - Скопировать файлы к себе на компьютер. Указать токен в файле commands.sh в поле <токен>. Запустить скрипт commands.sh в терминале.

2)  Скопировать файлы к себе на компьютер, установить зависимости из requirements.txt. Добавить в токен в скрипт note_bot.py или прокинуть в переменную окружения `MCC_TOKEN` при запуске скрипта.

3) Если хочется просто попробывать как работает бот без лишних усилий, вы можете написать мне в телеграмм @garick161, я запущу бота у себя и скину вам ссылку на бота.

![in_cabine](https://github.com/garick161/MCC_notes_bot/assets/114688542/654c71be-5cc0-4637-afd0-ad26251e76fb)
