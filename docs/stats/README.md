# Analytics Service

## Ответственность
- Сбор и агрегация статистики взаимодействий
- Генерация отчетов в реальном времени
- Хранение исторических данных
- Анализ паттернов поведения

## Границы сервиса
❗ Не имеет доступа к персональным данным  
❗ Не влияет на бизнес-логику приложения  
❗ Не участвует в цепочке запросов в реальном времени

```mermaid
erDiagram
    LIKE_STAT {
        uuid id PK
        uuid target_id
        string target_type
        uuid user_id FK
        datetime timestamp
        string reaction
        string device_hash
    }
    
    VIEW_STAT {
        uuid id PK
        uuid post_id FK
        uuid user_id FK
        datetime timestamp
        string ip_hash
        integer duration
    }
    
    COMMENT_STAT {
        uuid id PK
        uuid comment_id FK
        datetime timestamp
        string operation
        uuid user_id FK
        string source
    }
    
    POST ||--o{ VIEW_STAT : tracks
    COMMENT ||--o{ COMMENT_STAT : records
```