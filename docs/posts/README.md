# Content Service

## Ответственность
- Создание/редактирование постов и комментариев
- Генерация и валидация промокодов
- Модерация пользовательского контента
- Управление версиями контента

## Границы сервиса
❗ Не хранит статистику взаимодействий  
❗ Не управляет правами доступа  
❗ Не обрабатывает аутентификацию

```mermaid
erDiagram
    POST {
        uuid id PK
        uuid user_id FK
        string content
        datetime created_at
        datetime updated_at
        string status
        integer version
    }
    
    COMMENT {
        uuid id PK
        uuid post_id FK
        uuid user_id FK
        string text
        datetime created_at
        boolean is_edited
    }
    
    PROMOCODE {
        string code PK
        uuid user_id FK
        datetime expires_at
        boolean is_used
        datetime used_at
        integer discount
    }
    
    POST ||--o{ COMMENT : contains
    USER ||--o{ PROMOCODE : generates
```