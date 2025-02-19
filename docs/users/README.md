# User Service

## Ответственность
- Регистрация и аутентификация пользователей
- Управление ролями и правами доступа
- Хранение персональных данных
- Валидация учетных данных

## Границы сервиса
❗ Не имеет доступа к контенту пользователей  
❗ Не участвует в сборе статистики  
❗ Не обрабатывает платежи/промокоды напрямую

```mermaid
erDiagram
    USER {
        uuid id PK
        string email
        string password_hash
        datetime created_at
        datetime updated_at
        boolean is_active
    }
    
    ROLE {
        uuid id PK
        string name
        string description
        datetime created_at
        string permissions
        boolean is_default
    }
    
    USER_ROLE {
        uuid user_id FK
        uuid role_id FK
    }
    
    USER ||--o{ USER_ROLE : has
    ROLE ||--o{ USER_ROLE : assigned_to
```
