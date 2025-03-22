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
  -d '{"login": "login", "password": "password"}'
```

## Получение профиля:

```bash
curl -X GET http://localhost:5000/users/4 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MzI1ODU1MSwianRpIjoiOGEzOTVkYzItYTAyMi00ZDhmLWJjYjAtZTgxMjVhNTUzNWFlIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjQiLCJuYmYiOjE3NDMyNTg1NTEsImV4cCI6MTc0MzI1OTQ1MX0.gfnsyj2LHekL8OZFihGJYoMqZnXsOaO3FrzsQpvsNRQ"
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
be-my-fire@be-my-fire-x promos % docker-compose exec promo-service pytest service/tests/ -v
be-my-fire@be-my-fire-x promos % docker-compose exec post-service pytest service/tests/ -v
```

## Posts
**Создание поста:**
```bash
curl -X POST http://localhost:5000/posts \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Post",
    "description": "This is my first blog post",
    "is_private": false,
    "tags": ["blogging", "intro"]
  }'
```

**Получение поста:**
```bash
curl http://localhost:5000/posts/<post_id> \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Обновление поста:**
```bash
curl -X PUT http://localhost:5000/posts/<post_id> \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Post Title",
    "is_private": true
  }'
```

**Удаление поста:**
```bash
curl -X DELETE http://localhost:5000/posts/<post_id> \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Список постов:**
```bash
curl "http://localhost:5000/posts?page=2&per_page=5" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Promos
**Создание промокода:**
```bash
curl -X POST http://localhost:5000/promos \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Summer Sale",
    "discount": 20.5,
    "code": "SUMMER2024"
  }'
```

**Получение промокода:**
```bash
curl http://localhost:5000/promos/<promo_id> \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Обновление промокода:**
```bash
curl -X PUT http://localhost:5000/promos/<promo_id> \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "discount": 25.0,
    "code": "SUMMER25"
  }'
```

**Удаление промокода:**
```bash
curl -X DELETE http://localhost:5000/promos/<promo_id> \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Список промокодов:**
```bash
curl "http://localhost:5000/promos?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
