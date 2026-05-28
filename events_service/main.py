import grpc
from concurrent import futures
import pika
import json
import os
import uuid

import events_pb2
import events_pb2_grpc

from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/events_db")
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class EventModel(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    date = Column(String)
    location = Column(String)

Base.metadata.create_all(bind=engine)

class EventsService(events_pb2_grpc.EventsServiceServicer):
    def CreateEvent(self, request, context):
        db = SessionLocal()
        event_id = str(uuid.uuid4())
        
        new_event = EventModel(
            id=event_id, 
            title=request.title, 
            date=request.date, 
            location=request.location
        )
        db.add(new_event)
        db.commit()
        db.close()

        try:
            rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
            connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
            channel = connection.channel()
            channel.queue_declare(queue='notifications')
            
            event_data = {"id": event_id, "title": request.title, "location": request.location}
            channel.basic_publish(
                exchange='', 
                routing_key='notifications', 
                body=json.dumps(event_data)
            )
            print(f"Событие опубликовано в RabbitMQ: {event_data}")
            connection.close()
        except Exception as e:
            print(f"Ошибка отправки в RabbitMQ: {e}")

        return events_pb2.EventResponse(
            event=events_pb2.Event(id=event_id, title=request.title, date=request.date, location=request.location)
        )

    def GetEvents(self, request, context):
        db = SessionLocal()
        events = db.query(EventModel).all()
        db.close()
        
        event_list = [
            events_pb2.Event(id=e.id, title=e.title, date=e.date, location=e.location) 
            for e in events
        ]
        return events_pb2.EventListResponse(events=event_list)

# 3. Запуск сервера
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    events_pb2_grpc.add_EventsServiceServicer_to_server(EventsService(), server)
    
    server.add_insecure_port('[::]:8277') 
    print("Events Service (gRPC) запущен на порту 8277...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()