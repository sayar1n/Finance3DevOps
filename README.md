# Сборка и запуск
docker-compose up --build

# Тестирование
curl http://localhost:3001/users
curl http://localhost:3002/transactions

# Остановка  
docker-compose down

Далее требуется перезапуск

# Тестирование
curl http://localhost
curl http://localhost/users
curl http://localhost/transactions