"""Shared messaging utilities for RabbitMQ integration.

This module provides a message broker abstraction for asynchronous
communication between microservices using RabbitMQ as the underlying
message broker implementation.
"""

import json
import os
from typing import Any, Callable, Optional

import aio_pika
from aio_pika import ExchangeType, Message

from shared.logging_config import get_logger


logger = get_logger()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


class MessageBroker:
    """RabbitMQ connection manager.

    Manages connection lifecycle and message publishing/consuming
    operations for the hotel booking microservices.

    :ivar connection: RabbitMQ connection instance
    :ivar channel: RabbitMQ channel instance
    :ivar exchange: RabbitMQ topic exchange for events
    """

    def __init__(self):
        """Initialize message broker with default connection parameters."""
        self.connection: Optional[Any] = None
        self.channel: Optional[Any] = None
        self.exchange: Optional[Any] = None

    async def connect(self):
        """Establish connection to RabbitMQ.

        Creates a robust connection, channel, and declares the topic exchange
        for event routing. Logs warning if connection fails but does not raise
        exception to allow graceful degradation.

        :raises: None - failures are logged but not raised
        """
        try:
            self.connection = await aio_pika.connect_robust(RABBITMQ_URL)
            self.channel = await self.connection.channel()
            self.exchange = await self.channel.declare_exchange(
                "hotel_booking_events", ExchangeType.TOPIC, durable=True
            )
            logger.info("rabbitmq_connected", url=RABBITMQ_URL)
        except Exception as e:
            logger.warning("rabbitmq_connection_failed", error=str(e))

    async def publish(self, routing_key: str, message: dict):
        """Publish message to exchange.

        Serializes message to JSON and publishes to the topic exchange with
        the specified routing key. Automatically connects if not already
        connected.

        :param routing_key: Routing key for message routing
        :type routing_key: str
        :param message: Message payload as dictionary
        :type message: dict
        """
        if not self.exchange:
            await self.connect()

        if not self.exchange:
            logger.warning(
                "rabbitmq_unavailable_skipping_publish", routing_key=routing_key
            )
            return

        try:
            message_body = json.dumps(message).encode()
            await self.exchange.publish(
                Message(message_body, content_type="application/json"),
                routing_key=routing_key,
            )
            logger.info("message_published", routing_key=routing_key)
        except Exception as e:
            logger.error(
                "message_publish_failed", routing_key=routing_key, error=str(e)
            )

    async def subscribe(self, queue_name: str, routing_key: str, callback: Callable):
        """Subscribe to queue and consume messages.

        Declares a durable queue, binds it to the exchange with the routing
        key, and starts consuming messages. Each message is passed to the
        callback function after JSON deserialization.

        :param queue_name: Name of the queue to declare and consume from
        :type queue_name: str
        :param routing_key: Routing key pattern for message binding
        :type routing_key: str
        :param callback: Async function to process received messages
        :type callback: Callable
        """
        if not self.channel:
            await self.connect()

        if not self.channel:
            logger.warning("rabbitmq_unavailable_skipping_subscribe", queue=queue_name)
            return

        try:
            queue = await self.channel.declare_queue(queue_name, durable=True)
            await queue.bind(self.exchange, routing_key=routing_key)

            async def process_message(message: Any):
                async with message.process():
                    body = json.loads(message.body.decode())
                    logger.info("message_received", routing_key=routing_key)
                    await callback(body)

            await queue.consume(process_message)
            logger.info(
                "subscribed_to_queue", queue=queue_name, routing_key=routing_key
            )
        except Exception as e:
            logger.error("subscription_failed", queue=queue_name, error=str(e))

    async def close(self):
        """Close RabbitMQ connection.

        Gracefully closes the connection to RabbitMQ and logs the
        disconnection event.
        """
        if self.connection:
            await self.connection.close()
            logger.info("rabbitmq_disconnected")


broker = MessageBroker()
