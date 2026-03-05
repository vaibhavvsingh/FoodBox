from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from main import get_db
from models import User, Car, FoodItem, Order, OrderItem, Delivery, Payment, Subscription, DeliveryStatus, PaymentStatus, SubscriptionPlan
from schemas import (
    UserCreate, UserUpdate, UserResponse,
    CarCreate, CarResponse,
    FoodItemCreate, FoodItemUpdate, FoodItemResponse,
    OrderCreate, OrderUpdate, OrderResponse,
    DeliveryBase, DeliveryUpdate, DeliveryResponse,
    PaymentCreate, PaymentUpdate, PaymentResponse,
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse,
    Token
)
from auth import get_current_user, create_access_token
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

PRICES = {
    SubscriptionPlan.BASIC: 99.99,
    SubscriptionPlan.PREMIUM: 149.99,
    SubscriptionPlan.FAMILY: 249.99
}

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        phone=user.phone,
        address=user.address
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/token", response_model=Token)
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/users/me", response_model=UserResponse)
def update_current_user(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_update.email:
        current_user.email = user_update.email
    if user_update.username:
        current_user.username = user_update.username
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.phone:
        current_user.phone = user_update.phone
    if user_update.address:
        current_user.address = user_update.address
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(User).offset(skip).limit(limit).all()

@router.post("/cars", response_model=CarResponse)
def create_car(car: CarCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    new_car = Car(**car.dict())
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

@router.get("/cars", response_model=List[CarResponse])
def get_cars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Car).filter(Car.is_available == True).offset(skip).limit(limit).all()

@router.put("/cars/{car_id}", response_model=CarResponse)
def update_car(car_id: int, car_update: CarCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    car.plate_number = car_update.plate_number
    car.model = car_update.model
    car.capacity_kg = car_update.capacity_kg
    car.driver_name = car_update.driver_name
    car.driver_phone = car_update.driver_phone
    db.commit()
    db.refresh(car)
    return car

@router.post("/food-items", response_model=FoodItemResponse)
def create_food_item(item: FoodItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    new_item = FoodItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/food-items", response_model=List[FoodItemResponse])
def get_food_items(skip: int = 0, limit: int = 100, category: str = None, db: Session = Depends(get_db)):
    query = db.query(FoodItem).filter(FoodItem.is_available == True)
    if category:
        query = query.filter(FoodItem.category == category)
    return query.offset(skip).limit(limit).all()

@router.get("/food-items/{item_id}", response_model=FoodItemResponse)
def get_food_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(FoodItem).filter(FoodItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    return item

@router.put("/food-items/{item_id}", response_model=FoodItemResponse)
def update_food_item(item_id: int, item_update: FoodItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    item = db.query(FoodItem).filter(FoodItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    for key, value in item_update.dict(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

@router.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_amount = 0
    order_items_data = []
    
    for item in order.items:
        food_item = db.query(FoodItem).filter(FoodItem.id == item.food_item_id).first()
        if not food_item:
            raise HTTPException(status_code=404, detail=f"Food item {item.food_item_id} not found")
        if not food_item.is_available:
            raise HTTPException(status_code=400, detail=f"Food item {food_item.name} is not available")
        subtotal = food_item.price * item.quantity
        total_amount += subtotal
        order_items_data.append({
            "food_item_id": food_item.id,
            "quantity": item.quantity,
            "unit_price": food_item.price,
            "subtotal": subtotal
        })
    
    new_order = Order(
        user_id=current_user.id,
        delivery_address=order.delivery_address,
        notes=order.notes,
        total_amount=total_amount
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    for item_data in order_items_data:
        order_item = OrderItem(order_id=new_order.id, **item_data)
        db.add(order_item)
    
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/orders", response_model=List[OrderResponse])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        return db.query(Order).offset(skip).limit(limit).all()
    return db.query(Order).filter(Order.user_id == current_user.id).offset(skip).limit(limit).all()

@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not current_user.is_admin and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return order

@router.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not current_user.is_admin and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if order_update.status:
        order.status = order_update.status
    if order_update.delivery_address:
        order.delivery_address = order_update.delivery_address
    if order_update.notes:
        order.notes = order_update.notes
    
    db.commit()
    db.refresh(order)
    return order

@router.post("/deliveries", response_model=DeliveryResponse)
def create_delivery(delivery: DeliveryBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    order = db.query(Order).filter(Order.id == delivery.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    new_delivery = Delivery(
        order_id=delivery.order_id,
        car_id=delivery.car_id,
        status=DeliveryStatus.PENDING
    )
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    return new_delivery

@router.get("/deliveries", response_model=List[DeliveryResponse])
def get_deliveries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(Delivery).offset(skip).limit(limit).all()

@router.get("/orders/{order_id}/delivery", response_model=DeliveryResponse)
def get_order_delivery(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not current_user.is_admin and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery

@router.put("/deliveries/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(delivery_id: int, delivery_update: DeliveryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    if delivery_update.status:
        delivery.status = delivery_update.status
        if delivery_update.status == DeliveryStatus.DELIVERED:
            delivery.delivered_at = datetime.utcnow()
    if delivery_update.car_id:
        delivery.car_id = delivery_update.car_id
    if delivery_update.current_location_lat:
        delivery.current_location_lat = delivery_update.current_location_lat
    if delivery_update.current_location_lng:
        delivery.current_location_lng = delivery_update.current_location_lng
    
    db.commit()
    db.refresh(delivery)
    return delivery

@router.post("/payments", response_model=PaymentResponse)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not current_user.is_admin and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_payment = Payment(
        order_id=payment.order_id,
        user_id=current_user.id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        status=PaymentStatus.PENDING,
        transaction_id=f"TXN{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

@router.get("/payments", response_model=List[PaymentResponse])
def get_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        return db.query(Payment).offset(skip).limit(limit).all()
    return db.query(Payment).filter(Payment.user_id == current_user.id).offset(skip).limit(limit).all()

@router.put("/payments/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: int, payment_update: PaymentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment_update.status:
        payment.status = payment_update.status
    
    db.commit()
    db.refresh(payment)
    return payment

@router.post("/subscriptions", response_model=SubscriptionResponse)
def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Subscription).filter(Subscription.user_id == current_user.id, Subscription.is_active == True).first()
    if existing:
        raise HTTPException(status_code=400, detail="Active subscription already exists")
    
    monthly_price = PRICES.get(subscription.plan, 99.99)
    new_subscription = Subscription(
        user_id=current_user.id,
        plan=subscription.plan,
        monthly_price=monthly_price,
        meals_per_week=subscription.meals_per_week,
        protein_target_grams=subscription.protein_target_grams,
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
def get_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        return db.query(Subscription).offset(skip).limit(limit).all()
    return db.query(Subscription).filter(Subscription.user_id == current_user.id).offset(skip).limit(limit).all()

@router.get("/subscriptions/me", response_model=SubscriptionResponse)
def get_my_subscription(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id, Subscription.is_active == True).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription")
    return subscription

@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(subscription_id: int, subscription_update: SubscriptionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if subscription_update.plan:
        subscription.plan = subscription_update.plan
        subscription.monthly_price = PRICES.get(subscription_update.plan, 99.99)
    if subscription_update.meals_per_week:
        subscription.meals_per_week = subscription_update.meals_per_week
    if subscription_update.protein_target_grams:
        subscription.protein_target_grams = subscription_update.protein_target_grams
    if subscription_update.is_active is not None:
        subscription.is_active = subscription_update.is_active
    
    db.commit()
    db.refresh(subscription)
    return subscription
