from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import asyncio
import aio_pika
import json

app = FastAPI()

RABBIT_URL = os.environ.get("RABBIT_URL", "amqp://guest:guest@component1:5672/")
QUEUE_NAME = os.environ.get("QUEUE_NAME", "items_queue")

class Item(BaseModel):
    name: str
    description: str

async def get_connection():
    return await aio_pika.connect_robust(RABBIT_URL)

@app.post("/items")
async def publish_item(item: Item):
    try:
        connection = await get_connection()
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(item.dict()).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=QUEUE_NAME,
            )
        return {"status": "published"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))