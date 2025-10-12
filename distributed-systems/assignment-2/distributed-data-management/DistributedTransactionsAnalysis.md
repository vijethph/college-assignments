# Part D: Distributed Transactions Analysis

## E-commerce Order Workflow Example

Consider a typical e-commerce order placement involving three microservices:

### Services Involved

1. **OrderService**: Manages order creation and status
2. **PaymentService**: Processes payment transactions
3. **InventoryService**: Manages stock levels and reservations

![E-commerce Workflow](/mermaid1.png "E-commerce Workflow")

### Order Placement Workflow

1. Validate order details and customer information
2. Reserve inventory items
3. Process payment authorization
4. Confirm order and update inventory
5. Send confirmation notifications

## Transaction Management Approaches

### 1. ACID Transactions (Traditional Approach)

#### Implementation

```python
# Pseudocode for ACID transaction
def place_order_acid(order_data):
    with database.transaction():
        # All operations in single transaction
        order_id = create_order(order_data)
        reserve_inventory(order_data.items)
        charge_payment(order_data.payment_info)
        confirm_order(order_id)
        return order_id
```

![ACID Transactions](/mermaid2.png "ACID Transactions")

#### Problems in Distributed Systems

- **Single Point of Failure**: Central coordinator required
- **Distributed Lock Management**: Complex 2PC (Two-Phase Commit) protocol
- **Performance Bottlenecks**: Synchronous coordination across services
- **Availability Issues**: System blocked if any service is unavailable
- **Scalability Limitations**: Locks reduce concurrent processing capability

#### Why ACID is Problematic

1. **Network Latency**: Cross-service calls add significant delay
2. **Service Dependencies**: Failure of one service affects all others
3. **Lock Contention**: Resources locked for extended periods
4. **Deadlock Potential**: Circular dependencies between services

### 2. Saga Pattern (Distributed Transaction Alternative)

#### A. Orchestrated Saga

**Central Coordinator Approach**

```python
class OrderOrchestrator:
    def place_order(self, order_data):
        saga_id = generate_saga_id()

        try:
            # Step 1: Create Order
            order_id = self.order_service.create_order(order_data)
            self.log_saga_step(saga_id, "ORDER_CREATED", order_id)

            # Step 2: Reserve Inventory
            reservation_id = self.inventory_service.reserve_items(order_data.items)
            self.log_saga_step(saga_id, "INVENTORY_RESERVED", reservation_id)

            # Step 3: Process Payment
            payment_id = self.payment_service.charge_payment(order_data.payment_info)
            self.log_saga_step(saga_id, "PAYMENT_PROCESSED", payment_id)

            # Step 4: Confirm Order
            self.order_service.confirm_order(order_id)
            self.log_saga_step(saga_id, "ORDER_CONFIRMED", order_id)

            return order_id

        except PaymentFailedException:
            # Compensating transactions
            self.inventory_service.release_reservation(reservation_id)
            self.order_service.cancel_order(order_id)
            raise OrderProcessingException("Payment failed")

        except InventoryException:
            # Compensating transactions
            self.order_service.cancel_order(order_id)
            raise OrderProcessingException("Insufficient inventory")
```

**Advantages:**

- **Centralized Control**: Clear workflow visibility
- **Easy Monitoring**: Single point for saga status tracking
- **Simplified Error Handling**: Coordinator manages compensations
- **Business Logic Clarity**: Workflow steps explicitly defined

**Disadvantages:**

- **Single Point of Failure**: Coordinator becomes bottleneck
- **Tight Coupling**: Services depend on central coordinator
- **Complexity**: Coordinator must understand all service interactions

![Orchestrated Saga](/mermaid3.png "Orchestrated Saga")

#### B. Choreographed Saga

**Event-Driven Approach**

```python
# Order Service
class OrderService:
    def create_order(self, order_data):
        order_id = self.repository.save_order(order_data)
        self.event_bus.publish(OrderCreatedEvent(order_id, order_data))
        return order_id

    def handle_inventory_reserved(self, event):
        if event.success:
            self.event_bus.publish(ProcessPaymentEvent(event.order_id))
        else:
            self.cancel_order(event.order_id)

# Inventory Service
class InventoryService:
    def handle_order_created(self, event):
        try:
            reservation_id = self.reserve_items(event.order_data.items)
            self.event_bus.publish(InventoryReservedEvent(
                event.order_id, reservation_id, success=True
            ))
        except InsufficientStockException:
            self.event_bus.publish(InventoryReservedEvent(
                event.order_id, None, success=False
            ))

# Payment Service
class PaymentService:
    def handle_process_payment(self, event):
        try:
            payment_id = self.charge_payment(event.payment_info)
            self.event_bus.publish(PaymentProcessedEvent(
                event.order_id, payment_id, success=True
            ))
        except PaymentException:
            self.event_bus.publish(PaymentProcessedEvent(
                event.order_id, None, success=False
            ))
```

![Choreographed Saga](/mermaid4.png "Choreographed Saga")

**Advantages:**

- **Loose Coupling**: Services only know about events, not each other
- **High Availability**: No central coordinator dependency
- **Scalability**: Services can process events independently
- **Flexibility**: Easy to add new services to workflow

**Disadvantages:**

- **Complex Debugging**: Distributed workflow harder to trace
- **Event Ordering**: Potential race conditions between events
- **Circular Dependencies**: Risk of infinite event loops

## Trade-off Analysis

### Consistency vs Availability

| Aspect                  | ACID Transactions | Orchestrated Saga | Choreographed Saga |
| ----------------------- | ----------------- | ----------------- | ------------------ |
| **Consistency**         | Strong (ACID)     | Eventual          | Eventual           |
| **Availability**        | Low (blocking)    | Medium            | High               |
| **Partition Tolerance** | Poor              | Good              | Excellent          |
| **Performance**         | Slow              | Medium            | Fast               |

### Complexity vs Control

| Aspect                        | ACID | Orchestrated | Choreographed |
| ----------------------------- | ---- | ------------ | ------------- |
| **Implementation Complexity** | Low  | Medium       | High          |
| **Operational Complexity**    | High | Medium       | Medium        |
| **Debugging Difficulty**      | Low  | Medium       | High          |
| **Business Logic Clarity**    | High | High         | Medium        |

### Fault Tolerance

| Failure Scenario        | ACID Response            | Saga Response                     |
| ----------------------- | ------------------------ | --------------------------------- |
| **Service Unavailable** | Block entire transaction | Continue with compensation        |
| **Network Partition**   | Transaction fails        | Eventual consistency maintained   |
| **Partial Success**     | Complete rollback        | Compensating actions              |
| **Data Corruption**     | Immediate consistency    | Manual intervention may be needed |

## When to Use Each Approach

![Approach Workflow](/mermaid5.png "Approach Workflow")

### ACID Transactions

- **Suitable for:**

  - Single-service operations
  - Financial systems requiring strict consistency
  - Small-scale applications
  - Operations with low latency requirements

- **Avoid when:**
  - Services are distributed across networks
  - High availability is critical
  - System needs to scale horizontally

### Orchestrated Saga

- **Suitable for:**

  - Complex business workflows
  - Need for centralized monitoring
  - Clear error handling requirements
  - Team prefers explicit control flow

- **Avoid when:**
  - High availability is critical
  - Services are owned by different teams
  - Workflow changes frequently

### Choreographed Saga

- **Suitable for:**

  - High-throughput systems
  - Microservices architectures
  - Event-driven systems
  - Independent service deployment

- **Avoid when:**
  - Complex business rules
  - Need for centralized control
  - Debugging capabilities are limited

## MongoDB-Specific Considerations

### MongoDB Transactions (4.0+)

- **Multi-document ACID transactions** within single replica set
- **Cross-shard transactions** in sharded clusters (4.2+)
- **Performance impact** due to distributed coordination
- **Best practices**: Keep transactions short and simple

### Saga Implementation with MongoDB

```python
# Saga state tracking in MongoDB
class SagaStateManager:
    def __init__(self, mongodb_client):
        self.db = mongodb_client.saga_db
        self.collection = self.db.saga_states

    def start_saga(self, saga_id, workflow_steps):
        saga_state = {
            "_id": saga_id,
            "status": "IN_PROGRESS",
            "steps": workflow_steps,
            "completed_steps": [],
            "failed_step": None,
            "created_at": datetime.now()
        }
        self.collection.insert_one(saga_state)

    def complete_step(self, saga_id, step_name, result):
        self.collection.update_one(
            {"_id": saga_id},
            {
                "$push": {"completed_steps": {"step": step_name, "result": result}},
                "$set": {"updated_at": datetime.now()}
            }
        )

    def mark_failed(self, saga_id, failed_step, error):
        self.collection.update_one(
            {"_id": saga_id},
            {
                "$set": {
                    "status": "FAILED",
                    "failed_step": failed_step,
                    "error": str(error),
                    "updated_at": datetime.now()
                }
            }
        )
```

## Conclusion

The choice between ACID transactions and Saga patterns depends on specific system requirements:

- **For strict consistency and simple workflows**: Traditional ACID transactions
- **For complex workflows with centralized control**: Orchestrated Sagas
- **For high availability and loose coupling**: Choreographed Sagas

In distributed systems, **eventual consistency with Saga patterns** often provides better scalability and availability than strict ACID consistency, aligning with the CAP theorem principles demonstrated in our MongoDB replica set experiments.
