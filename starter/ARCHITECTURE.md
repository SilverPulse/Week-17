# Архитектура

## Обзор
Система состоит из следующих микросервисов:
1. **API Gateway**: Единая точка входа для клиентов и маршрутизация запросов.
2. **Events Service (`events-svc-s18`)**: Создание и управление мероприятиями.
3. **Notification Service**: Асинхронная отправка уведомлений о новых мероприятиях.

## Диаграмма взаимодействия
[Клиент] -> (REST) -> [API Gateway] -> (gRPC) -> [Events Service] (PostgreSQL)
                                                       |
                                                  (RabbitMQ)
                                                       |
                                                       v
                                            [Notification Service]

## Технологический стек
- **Язык**: Python (FastAPI для Gateway, gRPC для микросервисов)
- **База данных**: PostgreSQL
- **Очередь сообщений**: RabbitMQ
- **Контейнеризация**: Docker + Compose

## Решения
- Выбран **REST** для внешнего API (`/api/events`), так как это удобно для интеграции с фронтендом.
- Выбран **gRPC** для внутреннего общения между API Gateway и Events Service, так как важна скорость и строгий контракт данных `events.v1`.
- Выбран **RabbitMQ** для передачи событий от Events Service к Notification Service, чтобы обеспечить слабую связность (Coupling) и отказоустойчивость.