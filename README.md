# SOA

Прихач Дарья Валерьевна, группа БПМИ225, социальная сеть

## Собрать все воедино (как необычно ага)
```bash
 docker-compose up --build
```

## Регистрация

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"login": "testuser", "password": "testpass", "email": "test@example.com"}'
```

## Аутентификация:

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"login": "testuser", "password": "testpass"}'
```

## Получение профиля:

```bash
curl -X GET http://localhost:5000/users/<user_id> \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

## Обновление профиля:

```bash
curl -X PUT http://localhost:5000/users/<user_id> \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe"}'
```


## Посмотреть содержимое базки

Можно при большом желании задать  __tablename__ = 'users' в models.py. Но я в этом особо много смысла не вижу. Поэтому чтобы посмотреть содержимое надо 

### 1. Подключится к контейнеру с БД:
```bash
docker exec -it <имя_контейнера_БД> psql -U user users
```

Имя контейнера можно узнать командой:
```bash
docker ps --filter "name=db"
```

У меня это например:
```bash
docker exec -it rest-api-db-1 psql -U user users
```

### 2. В консоли PostgreSQL:
```sql
-- Показать все таблицы
\dt

-- Посмотреть содержимое таблицы user (если __tablename__ определен, то по идее можно и без "" просто user)
SELECT * FROM "user";

-- Показать структуру таблицы
\d users
```

## TESTS

Запустить сервис и запуск тестов:

```bash
docker-compose exec user-service pytest tests/ -v
docker-compose exec api-gateway pytest tests/ -v
```