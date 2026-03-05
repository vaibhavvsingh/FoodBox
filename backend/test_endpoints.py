import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use a separate test database
TEST_DB = "./test_foodbox.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from models import Base
from main import app, get_db


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


# ─── Helper ──────────────────────────────────────────────────────────────────

def register_user(username="testuser", email="test@example.com", password="password123"):
    return client.post("/register", json={
        "username": username,
        "email": email,
        "password": password,
        "full_name": "Test User",
        "phone": "1234567890",
        "address": "123 Test St"
    })


def get_token(username="testuser", password="password123"):
    resp = client.post("/token", params={"username": username, "password": password})
    return resp.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def create_admin_user():
    """Register a user and promote to admin directly in DB."""
    register_user(username="admin", email="admin@example.com", password="admin123")
    db = TestingSessionLocal()
    from models import User
    user = db.query(User).filter(User.username == "admin").first()
    user.is_admin = True
    db.commit()
    db.close()
    return get_token("admin", "admin123")


# ─── Root & Health ───────────────────────────────────────────────────────────

class TestRootAndHealth:
    def test_root(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json() == {"message": "Welcome to FoodBox API"}

    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "healthy"}


# ─── Auth: Register & Login ─────────────────────────────────────────────────

class TestAuth:
    def test_register_success(self):
        resp = register_user()
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data

    def test_register_duplicate_email(self):
        register_user()
        resp = register_user(username="other", email="test@example.com")
        assert resp.status_code == 400
        assert "Email already registered" in resp.json()["detail"]

    def test_register_duplicate_username(self):
        register_user()
        resp = register_user(username="testuser", email="other@example.com")
        assert resp.status_code == 400
        assert "Username already taken" in resp.json()["detail"]

    def test_login_success(self):
        register_user()
        resp = client.post("/token", params={"username": "testuser", "password": "password123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        register_user()
        resp = client.post("/token", params={"username": "testuser", "password": "wrong"})
        assert resp.status_code == 401

    def test_login_nonexistent_user(self):
        resp = client.post("/token", params={"username": "noone", "password": "pass"})
        assert resp.status_code == 401


# ─── Users ───────────────────────────────────────────────────────────────────

class TestUsers:
    def test_get_current_user(self):
        register_user()
        token = get_token()
        resp = client.get("/users/me", headers=auth_header(token))
        assert resp.status_code == 200
        assert resp.json()["username"] == "testuser"

    def test_get_current_user_unauthorized(self):
        resp = client.get("/users/me")
        assert resp.status_code == 401

    def test_update_current_user(self):
        register_user()
        token = get_token()
        resp = client.put("/users/me", json={"full_name": "Updated Name"}, headers=auth_header(token))
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Updated Name"

    def test_list_users_as_admin(self):
        admin_token = create_admin_user()
        register_user()
        resp = client.get("/users", headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_list_users_forbidden_for_non_admin(self):
        register_user()
        token = get_token()
        resp = client.get("/users", headers=auth_header(token))
        assert resp.status_code == 403


# ─── Cars ────────────────────────────────────────────────────────────────────

class TestCars:
    def test_create_car_as_admin(self):
        admin_token = create_admin_user()
        resp = client.post("/cars", json={
            "plate_number": "ABC-1234",
            "model": "Toyota Hiace",
            "capacity_kg": 100.0,
            "driver_name": "John",
            "driver_phone": "555-0001"
        }, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["plate_number"] == "ABC-1234"

    def test_create_car_forbidden_for_non_admin(self):
        register_user()
        token = get_token()
        resp = client.post("/cars", json={
            "plate_number": "XYZ-9999",
            "model": "Van",
        }, headers=auth_header(token))
        assert resp.status_code == 403

    def test_list_cars(self):
        admin_token = create_admin_user()
        client.post("/cars", json={
            "plate_number": "LIST-001",
            "model": "Ford Transit",
        }, headers=auth_header(admin_token))
        resp = client.get("/cars")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_update_car(self):
        admin_token = create_admin_user()
        create_resp = client.post("/cars", json={
            "plate_number": "UPD-001",
            "model": "Old Model",
        }, headers=auth_header(admin_token))
        car_id = create_resp.json()["id"]
        resp = client.put(f"/cars/{car_id}", json={
            "plate_number": "UPD-001",
            "model": "New Model",
        }, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["model"] == "New Model"

    def test_update_car_not_found(self):
        admin_token = create_admin_user()
        resp = client.put("/cars/9999", json={
            "plate_number": "X", "model": "X"
        }, headers=auth_header(admin_token))
        assert resp.status_code == 404


# ─── Food Items ──────────────────────────────────────────────────────────────

def create_food_item(admin_token, name="Chicken Bowl", price=12.99, category="bowls"):
    return client.post("/food-items", json={
        "name": name,
        "description": f"Delicious {name}",
        "price": price,
        "protein_grams": 35.0,
        "calories": 450,
        "category": category,
        "image_url": "https://example.com/img.jpg"
    }, headers=auth_header(admin_token))


class TestFoodItems:
    def test_create_food_item(self):
        admin_token = create_admin_user()
        resp = create_food_item(admin_token)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Chicken Bowl"

    def test_create_food_item_forbidden_for_non_admin(self):
        register_user()
        token = get_token()
        resp = client.post("/food-items", json={
            "name": "X", "price": 1.0
        }, headers=auth_header(token))
        assert resp.status_code == 403

    def test_list_food_items(self):
        admin_token = create_admin_user()
        create_food_item(admin_token, name="Item A", category="bowls")
        create_food_item(admin_token, name="Item B", category="drinks")
        resp = client.get("/food-items")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_food_items_by_category(self):
        admin_token = create_admin_user()
        create_food_item(admin_token, name="Item A", category="bowls")
        create_food_item(admin_token, name="Item B", category="drinks")
        resp = client.get("/food-items", params={"category": "bowls"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["category"] == "bowls"

    def test_get_food_item(self):
        admin_token = create_admin_user()
        item = create_food_item(admin_token).json()
        resp = client.get(f"/food-items/{item['id']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Chicken Bowl"

    def test_get_food_item_not_found(self):
        resp = client.get("/food-items/9999")
        assert resp.status_code == 404

    def test_update_food_item(self):
        admin_token = create_admin_user()
        item = create_food_item(admin_token).json()
        resp = client.put(f"/food-items/{item['id']}", json={
            "price": 15.99
        }, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["price"] == 15.99

    def test_update_food_item_not_found(self):
        admin_token = create_admin_user()
        resp = client.put("/food-items/9999", json={"price": 1.0}, headers=auth_header(admin_token))
        assert resp.status_code == 404


# ─── Orders ──────────────────────────────────────────────────────────────────

class TestOrders:
    def _setup_order_data(self):
        admin_token = create_admin_user()
        item = create_food_item(admin_token).json()
        register_user()
        user_token = get_token()
        return admin_token, item, user_token

    def test_create_order(self):
        admin_token, item, user_token = self._setup_order_data()
        resp = client.post("/orders", json={
            "delivery_address": "456 Delivery Ave",
            "notes": "Ring the bell",
            "items": [{"food_item_id": item["id"], "quantity": 2}]
        }, headers=auth_header(user_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["delivery_address"] == "456 Delivery Ave"
        assert data["total_amount"] == item["price"] * 2

    def test_create_order_item_not_found(self):
        register_user()
        user_token = get_token()
        resp = client.post("/orders", json={
            "delivery_address": "Addr",
            "items": [{"food_item_id": 9999, "quantity": 1}]
        }, headers=auth_header(user_token))
        assert resp.status_code == 404

    def test_list_orders_user_sees_own(self):
        admin_token, item, user_token = self._setup_order_data()
        client.post("/orders", json={
            "delivery_address": "Addr",
            "items": [{"food_item_id": item["id"], "quantity": 1}]
        }, headers=auth_header(user_token))
        resp = client.get("/orders", headers=auth_header(user_token))
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_orders_admin_sees_all(self):
        admin_token, item, user_token = self._setup_order_data()
        client.post("/orders", json={
            "delivery_address": "Addr",
            "items": [{"food_item_id": item["id"], "quantity": 1}]
        }, headers=auth_header(user_token))
        resp = client.get("/orders", headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_order(self):
        admin_token, item, user_token = self._setup_order_data()
        order = client.post("/orders", json={
            "delivery_address": "Addr",
            "items": [{"food_item_id": item["id"], "quantity": 1}]
        }, headers=auth_header(user_token)).json()
        resp = client.get(f"/orders/{order['id']}", headers=auth_header(user_token))
        assert resp.status_code == 200

    def test_get_order_not_found(self):
        register_user()
        token = get_token()
        resp = client.get("/orders/9999", headers=auth_header(token))
        assert resp.status_code == 404

    def test_update_order(self):
        admin_token, item, user_token = self._setup_order_data()
        order = client.post("/orders", json={
            "delivery_address": "Addr",
            "items": [{"food_item_id": item["id"], "quantity": 1}]
        }, headers=auth_header(user_token)).json()
        resp = client.put(f"/orders/{order['id']}", json={
            "status": "confirmed",
            "delivery_address": "New Addr"
        }, headers=auth_header(user_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "confirmed"


# ─── Deliveries ──────────────────────────────────────────────────────────────

class TestDeliveries:
    def _setup_delivery_data(self):
        admin_token = create_admin_user()
        item = create_food_item(admin_token).json()
        register_user()
        user_token = get_token()
        order = client.post("/orders", json={
            "delivery_address": "Addr",
            "items": [{"food_item_id": item["id"], "quantity": 1}]
        }, headers=auth_header(user_token)).json()
        car = client.post("/cars", json={
            "plate_number": "DEL-001",
            "model": "Van",
        }, headers=auth_header(admin_token)).json()
        return admin_token, user_token, order, car

    def test_create_delivery(self):
        admin_token, user_token, order, car = self._setup_delivery_data()
        resp = client.post("/deliveries", json={
            "order_id": order["id"],
            "car_id": car["id"]
        }, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "pending"

    def test_create_delivery_forbidden_for_non_admin(self):
        admin_token, user_token, order, car = self._setup_delivery_data()
        resp = client.post("/deliveries", json={
            "order_id": order["id"],
        }, headers=auth_header(user_token))
        assert resp.status_code == 403

    def test_list_deliveries(self):
        admin_token, user_token, order, car = self._setup_delivery_data()
        client.post("/deliveries", json={
            "order_id": order["id"],
            "car_id": car["id"]
        }, headers=auth_header(admin_token))
        resp = client.get("/deliveries", headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_order_delivery(self):
        admin_token, user_token, order, car = self._setup_delivery_data()
        client.post("/deliveries", json={
            "order_id": order["id"],
            "car_id": car["id"]
        }, headers=auth_header(admin_token))
        resp = client.get(f"/orders/{order['id']}/delivery", headers=auth_header(user_token))
        assert resp.status_code == 200

    def test_update_delivery_status(self):
        admin_token, user_token, order, car = self._setup_delivery_data()
        delivery = client.post("/deliveries", json={
            "order_id": order["id"],
            "car_id": car["id"]
        }, headers=auth_header(admin_token)).json()
        resp = client.put(f"/deliveries/{delivery['id']}", json={
            "status": "out_for_delivery",
            "current_location_lat": 40.7128,
            "current_location_lng": -74.0060
        }, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "out_for_delivery"

    def test_update_delivery_to_delivered(self):
        admin_token, user_token, order, car = self._setup_delivery_data()
        delivery = client.post("/deliveries", json={
            "order_id": order["id"],
            "car_id": car["id"]
        }, headers=auth_header(admin_token)).json()
        resp = client.put(f"/deliveries/{delivery['id']}", json={
            "status": "delivered"
        }, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "delivered"
        assert resp.json()["delivered_at"] is not None


# ─── Payments ────────────────────────────────────────────────────────────────

class TestPayments:
    def _setup_payment_data(self):
        admin_token = create_admin_user()
        item = create_food_item(admin_token).json()
        register_user()
        user_token = get_token()
        order = client.post("/orders", json={
            "delivery_address": "Addr",
            "items": [{"food_item_id": item["id"], "quantity": 1}]
        }, headers=auth_header(user_token)).json()
        return admin_token, user_token, order

    def test_create_payment(self):
        admin_token, user_token, order = self._setup_payment_data()
        resp = client.post("/payments", json={
            "order_id": order["id"],
            "amount": order["total_amount"],
            "payment_method": "credit_card"
        }, headers=auth_header(user_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "pending"
        assert resp.json()["transaction_id"].startswith("TXN")

    def test_create_payment_order_not_found(self):
        register_user()
        user_token = get_token()
        resp = client.post("/payments", json={
            "order_id": 9999,
            "amount": 10.0,
            "payment_method": "credit_card"
        }, headers=auth_header(user_token))
        assert resp.status_code == 404

    def test_list_payments(self):
        admin_token, user_token, order = self._setup_payment_data()
        client.post("/payments", json={
            "order_id": order["id"],
            "amount": order["total_amount"],
            "payment_method": "credit_card"
        }, headers=auth_header(user_token))
        resp = client.get("/payments", headers=auth_header(user_token))
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_update_payment_status(self):
        admin_token, user_token, order = self._setup_payment_data()
        payment = client.post("/payments", json={
            "order_id": order["id"],
            "amount": order["total_amount"],
            "payment_method": "credit_card"
        }, headers=auth_header(user_token)).json()
        resp = client.put(f"/payments/{payment['id']}", json={
            "status": "completed"
        }, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_update_payment_forbidden_for_non_admin(self):
        admin_token, user_token, order = self._setup_payment_data()
        payment = client.post("/payments", json={
            "order_id": order["id"],
            "amount": 10.0,
            "payment_method": "credit_card"
        }, headers=auth_header(user_token)).json()
        resp = client.put(f"/payments/{payment['id']}", json={
            "status": "completed"
        }, headers=auth_header(user_token))
        assert resp.status_code == 403


# ─── Subscriptions ───────────────────────────────────────────────────────────

class TestSubscriptions:
    def test_create_subscription(self):
        register_user()
        token = get_token()
        resp = client.post("/subscriptions", json={
            "plan": "premium",
            "meals_per_week": 14,
            "protein_target_grams": 200
        }, headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["plan"] == "premium"
        assert data["monthly_price"] == 149.99
        assert data["is_active"] is True

    def test_create_duplicate_subscription(self):
        register_user()
        token = get_token()
        client.post("/subscriptions", json={
            "plan": "basic", "meals_per_week": 7, "protein_target_grams": 150
        }, headers=auth_header(token))
        resp = client.post("/subscriptions", json={
            "plan": "premium", "meals_per_week": 14, "protein_target_grams": 200
        }, headers=auth_header(token))
        assert resp.status_code == 400
        assert "Active subscription already exists" in resp.json()["detail"]

    def test_get_my_subscription(self):
        register_user()
        token = get_token()
        client.post("/subscriptions", json={
            "plan": "family", "meals_per_week": 21, "protein_target_grams": 180
        }, headers=auth_header(token))
        resp = client.get("/subscriptions/me", headers=auth_header(token))
        assert resp.status_code == 200
        assert resp.json()["plan"] == "family"
        assert resp.json()["monthly_price"] == 249.99

    def test_get_my_subscription_none(self):
        register_user()
        token = get_token()
        resp = client.get("/subscriptions/me", headers=auth_header(token))
        assert resp.status_code == 404

    def test_list_subscriptions(self):
        register_user()
        token = get_token()
        client.post("/subscriptions", json={
            "plan": "basic", "meals_per_week": 7, "protein_target_grams": 150
        }, headers=auth_header(token))
        resp = client.get("/subscriptions", headers=auth_header(token))
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_update_subscription(self):
        register_user()
        token = get_token()
        sub = client.post("/subscriptions", json={
            "plan": "basic", "meals_per_week": 7, "protein_target_grams": 150
        }, headers=auth_header(token)).json()
        admin_token = create_admin_user()
        resp = client.put(f"/subscriptions/{sub['id']}", json={
            "plan": "premium",
            "meals_per_week": 14
        }, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["plan"] == "premium"
        assert resp.json()["monthly_price"] == 149.99

    def test_deactivate_subscription(self):
        register_user()
        token = get_token()
        sub = client.post("/subscriptions", json={
            "plan": "basic", "meals_per_week": 7, "protein_target_grams": 150
        }, headers=auth_header(token)).json()
        admin_token = create_admin_user()
        resp = client.put(f"/subscriptions/{sub['id']}", json={
            "is_active": False
        }, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False
