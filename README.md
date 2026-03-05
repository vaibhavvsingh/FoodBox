# FoodBox API

A FastAPI-based backend for a food order and delivery platform specializing in healthy high-protein meal subscriptions.

## Features

- **User Authentication** - JWT-based auth with registration and login
- **Food Management** - Menu items with nutritional info (protein, calories)
- **Order System** - Create and manage food orders
- **Delivery Tracking** - Real-time delivery status and location updates
- **Payment Processing** - Payment handling with transaction tracking
- **Monthly Subscriptions** - Three subscription tiers (Basic, Premium, Family) with customizable protein targets

## Tech Stack

- FastAPI
- SQLAlchemy (SQLite)
- Pydantic
- JWT Authentication
- Passlib (Bcrypt)

## Installation

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Register a new user | No |
| POST | `/token` | Login and get JWT token | No |

### Users

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/users/me` | Get current user profile | Yes |
| PUT | `/users/me` | Update current user profile | Yes |
| GET | `/users` | List all users (admin only) | Yes |

### Food Items

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/food-items` | Create food item (admin) | Yes |
| GET | `/food-items` | List available food items | No |
| GET | `/food-items/{item_id}` | Get food item details | No |
| PUT | `/food-items/{item_id}` | Update food item (admin) | Yes |

### Orders

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/orders` | Create a new order | Yes |
| GET | `/orders` | List user's orders | Yes |
| GET | `/orders/{order_id}` | Get order details | Yes |
| PUT | `/orders/{order_id}` | Update order status | Yes |

### Delivery

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/deliveries` | Create delivery (admin) | Yes |
| GET | `/deliveries` | List all deliveries (admin) | Yes |
| GET | `/orders/{order_id}/delivery` | Get delivery for order | Yes |
| PUT | `/deliveries/{delivery_id}` | Update delivery status | Yes |

### Payments

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/payments` | Create payment | Yes |
| GET | `/payments` | List user's payments | Yes |
| PUT | `/payments/{payment_id}` | Update payment status (admin) | Yes |

### Subscriptions

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/subscriptions` | Create subscription | Yes |
| GET | `/subscriptions` | List subscriptions | Yes |
| GET | `/subscriptions/me` | Get current user's active subscription | Yes |
| PUT | `/subscriptions/{subscription_id}` | Update subscription (admin) | Yes |

### Cars

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/cars` | Add delivery car (admin) | Yes |
| GET | `/cars` | List available cars | No |
| PUT | `/cars/{car_id}` | Update car details (admin) | Yes |

---

## Subscription Plans

| Plan | Price | Description |
|------|-------|-------------|
| Basic | $99.99/month | 7 meals/week, 150g protein target |
| Premium | $149.99/month | Enhanced meal options |
| Family | $249.99/month | Family-sized portions |

---

## Example Usage

### Register a User
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "address": "123 Main St"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=securepassword"
```

### Create an Order (with token)
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_address": "123 Main St",
    "notes": "Leave at door",
    "items": [
      {"food_item_id": 1, "quantity": 2},
      {"food_item_id": 3, "quantity": 1}
    ]
  }'
```

---

## Database Models

- **User** - User accounts with auth credentials
- **Car** - Delivery vehicles
- **FoodItem** - Menu items with nutritional data
- **Order** - Customer orders
- **OrderItem** - Individual items in an order
- **Delivery** - Delivery tracking info
- **Payment** - Payment transactions
- **Subscription** - Monthly meal subscriptions

---

## License

MIT
