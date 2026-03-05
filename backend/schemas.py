from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class SubscriptionPlan(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    FAMILY = "family"

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CarBase(BaseModel):
    plate_number: str
    model: str
    capacity_kg: float = 50.0
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None

class CarCreate(CarBase):
    pass

class CarResponse(CarBase):
    id: int
    is_available: bool
    created_at: datetime

    class Config:
        from_attributes = True

class FoodItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    protein_grams: float = 0
    calories: int = 0
    category: Optional[str] = None
    image_url: Optional[str] = None

class FoodItemCreate(FoodItemBase):
    pass

class FoodItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    protein_grams: Optional[float] = None
    calories: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None

class FoodItemResponse(FoodItemBase):
    id: int
    is_available: bool
    created_at: datetime

    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    food_item_id: int
    quantity: int = 1

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(BaseModel):
    id: int
    food_item_id: int
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    delivery_address: str
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: float
    delivery_address: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True

class DeliveryBase(BaseModel):
    order_id: int
    car_id: Optional[int] = None

class DeliveryUpdate(BaseModel):
    status: Optional[DeliveryStatus] = None
    car_id: Optional[int] = None
    current_location_lat: Optional[float] = None
    current_location_lng: Optional[float] = None

class DeliveryResponse(BaseModel):
    id: int
    order_id: int
    car_id: Optional[int]
    status: DeliveryStatus
    current_location_lat: Optional[float]
    current_location_lng: Optional[float]
    estimated_delivery_time: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    order_id: int
    amount: float
    payment_method: str

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None

class PaymentResponse(PaymentBase):
    id: int
    user_id: int
    status: PaymentStatus
    transaction_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class SubscriptionBase(BaseModel):
    plan: SubscriptionPlan
    meals_per_week: int = 7
    protein_target_grams: int = 150

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    plan: Optional[SubscriptionPlan] = None
    meals_per_week: Optional[int] = None
    protein_target_grams: Optional[int] = None
    is_active: Optional[bool] = None

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    monthly_price: float
    is_active: bool
    start_date: datetime
    end_date: Optional[datetime]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
