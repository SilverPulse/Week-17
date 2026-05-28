import pika
import json
import os
import sys
import time

def main():
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    
    connection = None
    for i in range(10):
        try:
            connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"Ожидание RabbitMQ... попытка {i+1}/10")
            time.sleep(3)
            
    if not connection:
        print("Ошибка: Не удалось подключиться к RabbitMQ")
        sys.exit(1)

    channel = connection.channel()
    channel.queue_declare(queue='notifications')

    def callback(ch, method, properties, body):
        event = json.loads(body)
        print("="*50)
        print(f"[🔔 УВЕДОМЛЕНИЕ] Создано новое мероприятие: '{event['title']}'!")
        print(f"[📍 ЛОКАЦИЯ] Место проведения: {event['location']}")
        print("="*50)

    channel.basic_consume(queue='notifications', on_message_callback=callback, auto_ack=True)

    print(' [*] Notification Service запущен. Ожидание сообщений...')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Прервано пользователем')
        sys.exit(0)