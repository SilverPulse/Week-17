from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import grpc
import os

import events_pb2
import events_pb2_grpc

app = FastAPI(title="Events API Gateway")

GRPC_HOST = os.getenv("GRPC_HOST", "localhost")
GRPC_PORT = os.getenv("GRPC_PORT", "8277")

class EventCreate(BaseModel):
    title: str
    date: str
    location: str

@app.post("/api/events")
def create_event(event: EventCreate):
    # Открываем gRPC канал до Events Service
    with grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}") as channel:
        stub = events_pb2_grpc.EventsServiceStub(channel)
        try:
            response = stub.CreateEvent(events_pb2.CreateEventRequest(
                title=event.title,
                date=event.date,
                location=event.location
            ))
            return {"status": "success", "id": response.event.id, "message": "Мероприятие создано"}
        except grpc.RpcError as e:
            raise HTTPException(status_code=500, detail=f"gRPC Error: {e.details()}")

@app.get("/api/events")
def get_events():
    with grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}") as channel:
        stub = events_pb2_grpc.EventsServiceStub(channel)
        try:
            response = stub.GetEvents(events_pb2.GetEventsRequest())
            return [{"id": e.id, "title": e.title, "date": e.date, "location": e.location} for e in response.events]
        except grpc.RpcError as e:
            raise HTTPException(status_code=500, detail=f"gRPC Error: {e.details()}")