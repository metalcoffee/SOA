# API Gateway Service

## Ответственность
- Маршрутизация запросов к соответствующим микросервисам
- Аутентификация и авторизация запросов
- Логирование и мониторинг трафика
- Ограничение скорости запросов (rate limiting)

## Границы сервиса
❗ Не содержит бизнес-логики приложения  
❗ Не хранит пользовательские данные  
❗ Не обрабатывает события аналитики

```mermaid
erDiagram
    API_ROUTE {
        uuid id PK
        string path
        string method
        string service_name
        integer timeout_ms
        boolean requires_auth
        datetime updated_at
    }
    
    REQUEST_LOG {
        uuid id PK
        string request_hash
        datetime timestamp
        integer status_code
        uuid user_id FK
        string endpoint
        float response_time
    }
    
    RATE_LIMIT {
        string key PK
        integer count
        datetime reset_time
        integer max_requests
        string window_type
    }
    
    API_ROUTE ||--o{ REQUEST_LOG : records
    API_ROUTE ||--o{ RATE_LIMIT : enforces

```