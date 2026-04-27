---
name: fastapi-templates
description: Create production-ready FastAPI projects with async patterns, dependency injection, and comprehensive error handling. Use when building new FastAPI applications or setting up backend API projects.
---

# FastAPI Project Templates

Production-ready FastAPI project structures with async patterns, dependency injection, middleware, and best practices for building high-performance APIs.

## When to Use This Skill

- Starting new FastAPI projects from scratch
- Implementing async REST APIs with Python
- Building high-performance web services and microservices
- Creating async applications with PostgreSQL, MongoDB
- Setting up API projects with proper structure and testing

## Core Concepts

### 1. Project Structure

**Recommended Layout:**
```
app/
├── api/                    # API routes
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── user.py
│   │   │   ├── auth.py
│   │   │   └── items.py
│   │   └── router.py
│   └── dependency.py       # Shared dependencies
├── core/                   # Core configuration
│   ├── config.py
│   ├── security.py
│   └── database.py
├── entity/                 # Database models (ORM)
│   ├── user.py
│   └── item.py
├── schema/                 # Pydantic schemas (DTO)
│   ├── user.py
│   └── item.py
├── service/                # Domain-oriented business logic
│   ├── user/
│   │   ├── user_service.py
│   │   └── user_repository.py
│   └── auth/
│       ├── auth_service.py
│       └── auth_repository.py
├── infra/                  # External infrastructure
│   ├── storage/
│   │   └── vector_storage.py
│   └── client/
│       └── openai_client.py
└── main.py                 # Application entry
```

### 2. Dependency Injection

FastAPI's built-in DI system using `Depends`:
- Database session management
- Authentication/authorization
- Shared business logic
- Configuration injection

### 3. Async Patterns

Proper async/await usage:
- Async route handlers
- Async database operations
- Async background tasks
- Async middleware

## 예시 코드

구현 시 아래 예시 파일을 참고한다.

| 파일 | 설명 |
|------|------|
| [`examples/app_setup.py`](examples/app_setup.py) | FastAPI 앱 설정 (lifespan, config, database) |
| [`examples/crud_repository.py`](examples/crud_repository.py) | Generic CRUD Repository |
| [`examples/service_layer.py`](examples/service_layer.py) | Service Layer |
| [`examples/api_endpoints.py`](examples/api_endpoints.py) | API Endpoints + Dependency Injection |
| [`examples/auth.py`](examples/auth.py) | JWT 인증/인가 (OAuth2) |
| [`examples/config.py`](examples/config.py) | YAML + Pydantic v2 Settings |
| [`examples/logging.py`](examples/logging.py) | 구조화 로깅 + Trace ID 미들웨어 |
| [`examples/testing_example.py`](examples/testing_example.py) | pytest async 테스트 설정 |

## Resources

- **references/fastapi-architecture.md**: Detailed architecture guide
- **references/async-best-practices.md**: Async/await patterns
- **references/testing-strategies.md**: Comprehensive testing guide
- **assets/project-template/**: Complete FastAPI project
- **assets/docker-compose.yml**: Development environment setup

## Best Practices

1. **Async All The Way**: Use async for database, external APIs
2. **Dependency Injection**: Leverage FastAPI's DI system
3. **Repository Pattern**: Separate data access from business logic
4. **Service Layer**: Keep business logic out of routes
5. **Pydantic Schemas**: Strong typing for request/response
6. **Error Handling**: Consistent error responses
7. **Testing**: Test all layers independently

## Common Pitfalls

- **Blocking Code in Async**: Using synchronous database drivers
- **No Service Layer**: Business logic in route handlers
- **Missing Type Hints**: Loses FastAPI's benefits
- **Ignoring Sessions**: Not properly managing database sessions
- **No Testing**: Skipping integration tests
- **Tight Coupling**: Direct database access in routes
