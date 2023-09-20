# Создание образа
docker build -t mcc_notes_bot .

# Запуск контейнера
docker run --name --rm mcc_bot -it -v $(pwd)/volumes:/volumes -e MCC_TOKEN=<токен> mcc_notes_bot
