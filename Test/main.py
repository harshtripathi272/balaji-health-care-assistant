# # main.py - Complete Business Management API
import os
import logging
import time
import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager

# # FastAPI imports
from fastapi import FastAPI, HTTPException, Query, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# # Pydantic imports
from pydantic import BaseModel, Field

# # Firebase imports
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Increment

# # Other imports
from dotenv import load_dotenv
import json

# # Load environment variables
load_dotenv()

# # ================================
# # LOGGING CONFIGURATION
# # ================================

# # Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

# Create specific loggers
app_logger = logging.getLogger("app")
api_logger = logging.getLogger("api")
db_logger = logging.getLogger("database")
auth_logger = logging.getLogger("auth")

# # ================================
# # CONFIGURATION
# # ================================

class Settings:
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    # SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

settings = Settings()

# # ================================
# # FIREBASE DATABASE SETUP
# # ================================

class FirebaseDB:
    def __init__(self):
        try:
            if not firebase_admin._apps:
                if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                    firebase_admin.initialize_app(cred)
                    db_logger.info("Firebase initialized with credentials file")
                else:
                    # Try to initialize with default credentials (for production)
                    firebase_admin.initialize_app()
                    db_logger.info("Firebase initialized with default credentials")
            
            self.db = firestore.client()
            db_logger.info("Firestore client created successfully")
        except Exception as e:
            db_logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    def get_collection(self, collection_name: str):
        return self.db.collection(collection_name)
    
    def get_document(self, collection_name: str, doc_id: str):
        return self.db.collection(collection_name).document(doc_id)

# Global database instance
firebase_db = FirebaseDB()

# # ================================
# # LOGGING UTILITIES
# # ================================

# class ActivityLogger:
#     @staticmethod
#     def log_activity(
#         action: str,
#         resource: str,
#         resource_id: str = None,
#         user: str = "system",
#         details: Dict[str, Any] = None,
#         request: Request = None
#     ):
#         """Log user activity with comprehensive details"""
#         try:
#             activity_data = {
#                 "timestamp": datetime.utcnow(),
#                 "action": action,  # CREATE, READ, UPDATE, DELETE
#                 "resource": resource,  # clients, orders, inventory, etc.
#                 "resource_id": resource_id,
#                 "user": user,
#                 "details": details or {},
#                 "ip_address": request.client.host if request else None,
#                 "user_agent": request.headers.get("user-agent") if request else None,
#                 "session_id": str(uuid.uuid4())
#             }
            
#             # Log to file
#             api_logger.info(f"ACTIVITY: {user} performed {action} on {resource} {resource_id or ''}")
            
#             # Store in Firebase for audit trail
#             firebase_db.get_collection("activity_logs").add(activity_data)
            
#         except Exception as e:
#             app_logger.error(f"Failed to log activity: {e}")

#     @staticmethod
#     def log_error(
#         error: str,
#         context: str,
#         user: str = "system",
#         request: Request = None,
#         exception: Exception = None
#     ):
#         """Log errors with context"""
#         try:
#             error_data = {
#                 "timestamp": datetime.utcnow(),
#                 "error": error,
#                 "context": context,
#                 "user": user,
#                 "ip_address": request.client.host if request else None,
#                 "exception_type": type(exception).__name__ if exception else None,
#                 "exception_details": str(exception) if exception else None,
#                 "session_id": str(uuid.uuid4())
#             }
            
#             # Log to file
#             app_logger.error(f"ERROR: {user} - {context} - {error}")
            
#             # Store in Firebase
#             firebase_db.get_collection("error_logs").add(error_data)
            
#         except Exception as e:
#             app_logger.error(f"Failed to log error: {e}")

# # ================================
# # AUTHENTICATION & USER MANAGEMENT
# # ================================

# security = HTTPBearer(auto_error=False)

# async def get_current_user(
#     request: Request,
#     credentials: HTTPAuthorizationCredentials = Depends(security)
# ) -> str:
#     """Extract user from request headers or token"""
#     try:
#         # Try to get user from custom header first
#         user = request.headers.get("X-User-ID") or request.headers.get("x-user-id")
        
#         if user:
#             auth_logger.info(f"User identified from header: {user}")
#             return user
        
#         # Try to get from Authorization header
#         if credentials:
#             # In a real app, you'd decode the JWT token here
#             # For now, we'll just use a simple approach
#             token = credentials.credentials
#             if token:
#                 # Simple token validation (replace with proper JWT validation)
#                 user = f"user_{token[:8]}"
#                 auth_logger.info(f"User identified from token: {user}")
#                 return user
        
#         # Default to system user
#         return "system"
        
#     except Exception as e:
#         auth_logger.error(f"Error getting current user: {e}")
#         return "system"

# # ================================
# # PYDANTIC MODELS
# # ================================

# Base Models
class TimestampMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Client Models
class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    PAN: str = Field(..., min_length=10, max_length=10)
    GST: str = Field(..., min_length=15, max_length=15)
    POC_name: str = Field(..., min_length=1, max_length=100)
    POC_contact: str = Field(..., min_length=10, max_length=15)
    address: str = Field(..., min_length=1, max_length=500)
    due_amount: int = Field(default=0, ge=0)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    PAN: Optional[str] = Field(None, min_length=10, max_length=10)
    GST: Optional[str] = Field(None, min_length=15, max_length=15)
    POC_name: Optional[str] = Field(None, min_length=1, max_length=100)
    POC_contact: Optional[str] = Field(None, min_length=10, max_length=15)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    due_amount: Optional[int] = Field(None, ge=0)

class Client(ClientBase, TimestampMixin):
    id: str

# # Employee Models
# class EmployeeBase(BaseModel):
#     name: str = Field(..., min_length=1, max_length=100)
#     phone: int = Field(..., ge=1000000000, le=9999999999)
#     paid: int = Field(default=0, ge=0)
#     collected: int = Field(default=0, ge=0)

# class EmployeeCreate(EmployeeBase):
#     pass

# class EmployeeUpdate(BaseModel):
#     name: Optional[str] = Field(None, min_length=1, max_length=100)
#     phone: Optional[int] = Field(None, ge=1000000000, le=9999999999)
#     paid: Optional[int] = Field(None, ge=0)
#     collected: Optional[int] = Field(None, ge=0)

# class Employee(EmployeeBase, TimestampMixin):
#     id: str

# # Expense Models
# class ExpenseBase(BaseModel):
#     amount: float = Field(..., gt=0)
#     category: str = Field(..., min_length=1, max_length=50)
#     remarks: str = Field(..., min_length=1, max_length=500)
#     paid_by: str = Field(..., min_length=1, max_length=100)

# class ExpenseCreate(ExpenseBase):
#     pass

# class ExpenseUpdate(BaseModel):
#     amount: Optional[float] = Field(None, gt=0)
#     category: Optional[str] = Field(None, min_length=1, max_length=50)
#     remarks: Optional[str] = Field(None, min_length=1, max_length=500)
#     paid_by: Optional[str] = Field(None, min_length=1, max_length=100)

# class Expense(ExpenseBase, TimestampMixin):
#     pass

# # Inventory Models
# class Batch(BaseModel):
#     batch_number: str = Field(..., min_length=1, max_length=50)
#     Expiry: str = Field(..., regex=r'^\d{2}/\d{4}$')  # MM/YYYY format
#     quantity: float = Field(..., gt=0)

# class InventoryItemBase(BaseModel):
#     name: str = Field(..., min_length=1, max_length=100)
#     category: str = Field(..., min_length=1, max_length=50)
#     stock_quantity: float = Field(..., ge=0)
#     low_stock: float = Field(..., ge=0)
#     batches: List[Batch] = Field(default=[])

# class InventoryItemCreate(InventoryItemBase):
#     pass

# class InventoryItemUpdate(BaseModel):
#     name: Optional[str] = Field(None, min_length=1, max_length=100)
#     category: Optional[str] = Field(None, min_length=1, max_length=50)
#     stock_quantity: Optional[float] = Field(None, ge=0)
#     low_stock: Optional[float] = Field(None, ge=0)
#     batches: Optional[List[Batch]] = None

# class InventoryItem(InventoryItemBase, TimestampMixin):
#     id: str

# # Order Models
class OrderItem(BaseModel):
    item_id: str = Field(..., min_length=1)
    item_name: str = Field(..., min_length=1, max_length=100)
    batch_number: str = Field(..., min_length=1, max_length=50)
    expiry: str = Field(..., regex=r'^\d{2}/\d{4}$')
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    tax: float = Field(default=0, ge=0, le=100)
    discount: float = Field(default=0, ge=0)

class OrderBase(BaseModel):
    invoice_number: str = Field(..., min_length=1, max_length=50)
    order_type: str = Field(..., regex=r'^(sell|purchase)$')
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None
    items: List[OrderItem] = Field(..., min_items=1)
    total_quantity: float = Field(..., gt=0)
    total_tax: float = Field(default=0, ge=0)
    total_amount: float = Field(..., gt=0)
    discount: float = Field(default=0, ge=0)
    discount_type: str = Field(default="percentage", regex=r'^(percentage|fixed)$')
    payment_status: str = Field(default="pending", regex=r'^(pending|paid|partial)$')
    payment_method: str = Field(..., min_length=1, max_length=50)
    amount_paid: float = Field(default=0, ge=0)
    amount_collected_by: Optional[str] = None
    status: str = Field(default="pending", regex=r'^(pending|processing|completed|cancelled)$')
    remarks: str = Field(default="", max_length=500)
    order_date: datetime
    challan_number: Optional[str] = None
    link: str = Field(default="", max_length=500)
    draft: bool = Field(default=False)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    payment_status: Optional[str] = Field(None, regex=r'^(pending|paid|partial)$')
    status: Optional[str] = Field(None, regex=r'^(pending|processing|completed|cancelled)$')
    amount_paid: Optional[float] = Field(None, ge=0)
    remarks: Optional[str] = Field(None, max_length=500)

class Order(OrderBase, TimestampMixin):
    created_by: str
    updated_by: str

# # Supplier Models
# class SupplierBase(BaseModel):
#     name: str = Field(..., min_length=1, max_length=100)
#     contact: str = Field(..., min_length=10, max_length=15)
#     address: str = Field(..., min_length=1, max_length=500)
#     due: int = Field(default=0, ge=0)

# class SupplierCreate(SupplierBase):
#     pass

# class SupplierUpdate(BaseModel):
#     name: Optional[str] = Field(None, min_length=1, max_length=100)
#     contact: Optional[str] = Field(None, min_length=10, max_length=15)
#     address: Optional[str] = Field(None, min_length=1, max_length=500)
#     due: Optional[int] = Field(None, ge=0)

# class Supplier(SupplierBase, TimestampMixin):
#     id: str

# # ================================
# # UTILITY FUNCTIONS
# # ================================

# class CounterService:
#     @staticmethod
#     async def get_next_id(collection_name: str, user: str = "system") -> str:
#         """Generate next ID for a collection"""
#         try:
#             counter_ref = firebase_db.get_document("doc_counters", collection_name)
#             counter_doc = counter_ref.get()
            
#             if counter_doc.exists:
#                 data = counter_doc.to_dict()
#                 last_id = data.get("last_id", "")
                
#                 if last_id:
#                     prefix = last_id[0]
#                     number = int(last_id[1:]) + 1
#                 else:
#                     prefix = collection_name[0].upper()
#                     number = 1
                
#                 new_id = f"{prefix}{number:04d}"
                
#                 counter_ref.update({
#                     "last_id": new_id,
#                     "total": Increment(1)
#                 })
                
#                 ActivityLogger.log_activity(
#                     action="GENERATE_ID",
#                     resource=collection_name,
#                     resource_id=new_id,
#                     user=user,
#                     details={"new_id": new_id, "counter": number}
#                 )
                
#                 return new_id
#             else:
#                 prefix = collection_name[0].upper()
#                 new_id = f"{prefix}0001"
#                 counter_ref.set({
#                     "last_id": new_id,
#                     "total": 1
#                 })
                
#                 ActivityLogger.log_activity(
#                     action="INITIALIZE_COUNTER",
#                     resource=collection_name,
#                     resource_id=new_id,
#                     user=user,
#                     details={"initial_id": new_id}
#                 )
                
#                 return new_id
                
#         except Exception as e:
#             ActivityLogger.log_error(
#                 error=f"Error generating ID for {collection_name}",
#                 context="CounterService.get_next_id",
#                 user=user,
#                 exception=e
#             )
#             raise HTTPException(status_code=500, detail=f"Error generating ID: {str(e)}")

#     @staticmethod
#     async def update_financial_summary(user: str = "system"):
#         """Update financial summary counters"""
#         try:
#             # Get all expenses
#             expenses_ref = firebase_db.get_collection("Expenses")
#             expenses = expenses_ref.stream()
#             total_expenses = sum(doc.to_dict().get("amount", 0) for doc in expenses)
            
#             # Get all orders (income)
#             orders_ref = firebase_db.get_collection("Orders")
#             orders = orders_ref.where("order_type", "==", "sell").stream()
#             total_income = sum(doc.to_dict().get("total_amount", 0) for doc in orders)
            
#             # Update financial summary
#             financial_ref = firebase_db.get_document("doc_counters", "financial_summary")
#             financial_data = {
#                 "total_income": total_income,
#                 "total_expenses": total_expenses,
#                 "net_profit": total_income - total_expenses,
#                 "last_updated_at": datetime.utcnow()
#             }
#             financial_ref.set(financial_data)
            
#             ActivityLogger.log_activity(
#                 action="UPDATE",
#                 resource="financial_summary",
#                 user=user,
#                 details=financial_data
#             )
            
#         except Exception as e:
#             ActivityLogger.log_error(
#                 error="Error updating financial summary",
#                 context="CounterService.update_financial_summary",
#                 user=user,
#                 exception=e
#             )

# def validate_email(email: str) -> bool:
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None

# def validate_phone(phone: str) -> bool:
#     digits = re.sub(r'\D', '', phone)
#     if len(digits) == 10 and digits[0] in '6789':
#         return True
#     elif len(digits) == 12 and digits.startswith('91') and digits[2] in '6789':
#         return True
#     return False

# def format_currency(amount: float, currency: str = "₹") -> str:
#     return f"{currency}{amount:,.2f}"

# def calculate_order_totals(items: List[Dict[str, Any]]) -> Dict[str, float]:
#     subtotal = 0
#     total_tax = 0
#     total_quantity = 0
    
#     for item in items:
#         quantity = item.get("quantity", 0)
#         price = item.get("price", 0)
#         tax = item.get("tax", 0)
#         discount = item.get("discount", 0)
        
#         item_total = quantity * price
#         item_discount = (item_total * discount) / 100
#         item_after_discount = item_total - item_discount
#         item_tax = (item_after_discount * tax) / 100
        
#         subtotal += item_after_discount
#         total_tax += item_tax
#         total_quantity += quantity
    
#     return {
#         "subtotal": subtotal,
#         "total_tax": total_tax,
#         "total_quantity": total_quantity,
#         "total_amount": subtotal + total_tax
#     }

# # ================================
# # FASTAPI APPLICATION SETUP
# # ================================

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     app_logger.info("Starting Business Management API")
    
#     # Initialize counters if they don't exist
#     try:
#         await initialize_counters()
#         app_logger.info("Counters initialized successfully")
#     except Exception as e:
#         app_logger.error(f"Failed to initialize counters: {e}")
    
#     yield
    
#     # Shutdown
#     app_logger.info("Shutting down Business Management API")

app = FastAPI(
    title="Business Management API",
    description="Complete internal business management tool API with Firebase backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    # lifespan=lifespan
)

# # Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app", "*"]
)

# # CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# # Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get user info
    user = request.headers.get("X-User-ID", "anonymous")
    
    # Log request start
    api_logger.info(
        f"REQUEST START: {user} - {request.method} {request.url.path} - "
        f"IP: {request.client.host} - UA: {request.headers.get('user-agent', 'Unknown')[:50]}"
    )
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log request completion
    api_logger.info(
        f"REQUEST END: {user} - {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Time: {process_time:.4f}s"
    )
    
    return response

# # Global exception handler
# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     user = request.headers.get("X-User-ID", "anonymous")
    
#     ActivityLogger.log_error(
#         error=str(exc),
#         context=f"{request.method} {request.url.path}",
#         user=user,
#         request=request,
#         exception=exc
#     )
    
#     return JSONResponse(
#         status_code=500,
#         content={"detail": "Internal server error", "error_id": str(uuid.uuid4())}
#     )

# # ================================
# # INITIALIZATION FUNCTIONS
# # ================================

# async def initialize_counters():
#     """Initialize counter documents"""
#     counters = {
#         "clients": {
#             "total": 0,
#             "last_id": "",
#             "total_due": 0
#         },
#         "employees": {
#             "total": 0,
#             "last_id": "",
#             "total_paid": 0,
#             "total_collected": 0
#         },
#         "expenses": {
#             "total": 0,
#             "total_amount": 0
#         },
#         "items": {
#             "total": 0,
#             "last_id": "",
#             "low_stock_count": 0
#         },
#         "financial_summary": {
#             "total_income": 0,
#             "total_expenses": 0,
#             "net_profit": 0,
#             "last_updated_at": datetime.utcnow()
#         }
#     }
    
#     for counter_name, data in counters.items():
#         try:
#             counter_ref = firebase_db.get_document("doc_counters", counter_name)
#             counter_doc = counter_ref.get()
            
#             if not counter_doc.exists:
#                 counter_ref.set(data)
#                 app_logger.info(f"Initialized {counter_name} counter")
#         except Exception as e:
#             app_logger.error(f"Failed to initialize {counter_name} counter: {e}")

# # ================================
# # API ROUTES
# # ================================

# # Root endpoints
# @app.get("/")
# async def root():
#     return {
#         "message": "Business Management API is running",
#         "version": "1.0.0",
#         "docs": "/docs",
#         "status": "operational"
#     }

# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "timestamp": datetime.utcnow().isoformat(),
#         "uptime": time.time()
#     }

# # ================================
# # CLIENT ROUTES
# # ================================

# @app.get("/api/v1/clients", response_model=List[Client])
# async def get_clients(
#     request: Request,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
#     search: Optional[str] = None,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         collection_ref = firebase_db.get_collection("Clients")
        
#         if search:
#             docs = collection_ref.stream()
#             clients = []
#             for doc in docs:
#                 data = doc.to_dict()
#                 if search.lower() in data.get("name", "").lower():
#                     clients.append(data)
#         else:
#             docs = collection_ref.offset(skip).limit(limit).stream()
#             clients = [doc.to_dict() for doc in docs]
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="clients",
#             user=current_user,
#             request=request,
#             details={"count": len(clients), "search": search, "skip": skip, "limit": limit}
#         )
        
#         return clients
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="get_clients",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/v1/clients", response_model=Client)
# async def create_client(
#     client: ClientCreate,
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         # Generate new ID
#         client_id = await CounterService.get_next_id("clients", current_user)
        
#         # Create client data
#         client_data = client.dict()
#         client_data.update({
#             "id": client_id,
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow()
#         })
        
#         # Save to Firebase
#         firebase_db.get_document("Clients", client_id).set(client_data)
        
#         # Update counters
#         counter_ref = firebase_db.get_document("doc_counters", "clients")
#         counter_doc = counter_ref.get()
#         if counter_doc.exists:
#             current_data = counter_doc.to_dict()
#             counter_ref.update({
#                 "total_due": current_data.get("total_due", 0) + client.due_amount
#             })
        
#         ActivityLogger.log_activity(
#             action="CREATE",
#             resource="clients",
#             resource_id=client_id,
#             user=current_user,
#             request=request,
#             details={"client_name": client.name, "due_amount": client.due_amount}
#         )
        
#         return client_data
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="create_client",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/v1/clients/{client_id}", response_model=Client)
# async def get_client(
#     client_id: str,
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         doc = firebase_db.get_document("Clients", client_id).get()
#         if not doc.exists:
#             raise HTTPException(status_code=404, detail="Client not found")
        
#         client_data = doc.to_dict()
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="clients",
#             resource_id=client_id,
#             user=current_user,
#             request=request,
#             details={"client_name": client_data.get("name")}
#         )
        
#         return client_data
#     except HTTPException:
#         raise
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="get_client",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.put("/api/v1/clients/{client_id}", response_model=Client)
# async def update_client(
#     client_id: str,
#     client_update: ClientUpdate,
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         doc_ref = firebase_db.get_document("Clients", client_id)
#         doc = doc_ref.get()
        
#         if not doc.exists:
#             raise HTTPException(status_code=404, detail="Client not found")
        
#         old_data = doc.to_dict()
        
#         # Update only provided fields
#         update_data = {k: v for k, v in client_update.dict().items() if v is not None}
#         update_data["updated_at"] = datetime.utcnow()
        
#         doc_ref.update(update_data)
        
#         # Get updated document
#         updated_doc = doc_ref.get()
#         updated_data = updated_doc.to_dict()
        
#         ActivityLogger.log_activity(
#             action="UPDATE",
#             resource="clients",
#             resource_id=client_id,
#             user=current_user,
#             request=request,
#             details={
#                 "client_name": updated_data.get("name"),
#                 "changes": update_data,
#                 "old_values": {k: old_data.get(k) for k in update_data.keys() if k != "updated_at"}
#             }
#         )
        
#         return updated_data
#     except HTTPException:
#         raise
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="update_client",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.delete("/api/v1/clients/{client_id}")
# async def delete_client(
#     client_id: str,
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         doc_ref = firebase_db.get_document("Clients", client_id)
#         doc = doc_ref.get()
        
#         if not doc.exists:
#             raise HTTPException(status_code=404, detail="Client not found")
        
#         client_data = doc.to_dict()
#         doc_ref.delete()
        
#         ActivityLogger.log_activity(
#             action="DELETE",
#             resource="clients",
#             resource_id=client_id,
#             user=current_user,
#             request=request,
#             details={"client_name": client_data.get("name"), "deleted_data": client_data}
#         )
        
#         return {"message": "Client deleted successfully"}
#     except HTTPException:
#         raise
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="delete_client",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# # ================================
# # EMPLOYEE ROUTES
# # ================================

# @app.get("/api/v1/employees", response_model=List[Employee])
# async def get_employees(
#     request: Request,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
#     search: Optional[str] = None,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         collection_ref = firebase_db.get_collection("Employees")
        
#         if search:
#             docs = collection_ref.stream()
#             employees = []
#             for doc in docs:
#                 data = doc.to_dict()
#                 if search.lower() in data.get("name", "").lower():
#                     employees.append(data)
#         else:
#             docs = collection_ref.offset(skip).limit(limit).stream()
#             employees = [doc.to_dict() for doc in docs]
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="employees",
#             user=current_user,
#             request=request,
#             details={"count": len(employees), "search": search}
#         )
        
#         return employees
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="get_employees",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/v1/employees", response_model=Employee)
# async def create_employee(
#     employee: EmployeeCreate,
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         # Generate new ID
#         employee_id = await CounterService.get_next_id("employees", current_user)
        
#         # Create employee data
#         employee_data = employee.dict()
#         employee_data.update({
#             "id": employee_id,
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow()
#         })
        
#         # Save to Firebase
#         firebase_db.get_document("Employees", employee_id).set(employee_data)
        
#         # Update counters
#         counter_ref = firebase_db.get_document("doc_counters", "employees")
#         counter_doc = counter_ref.get()
#         if counter_doc.exists:
#             counter_ref.update({
#                 "total_paid": Increment(employee.paid),
#                 "total_collected": Increment(employee.collected)
#             })
#         else:
#             counter_ref.set({
#                 "total": 1,
#                 "last_id": employee_id,
#                 "total_paid": employee.paid,
#                 "total_collected": employee.collected
#             })
        
#         ActivityLogger.log_activity(
#             action="CREATE",
#             resource="employees",
#             resource_id=employee_id,
#             user=current_user,
#             request=request,
#             details={"employee_name": employee.name, "phone": employee.phone}
#         )
        
#         return employee_data
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="create_employee",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.put("/api/v1/employees/{employee_id}/payment")
# async def update_employee_payment(
#     employee_id: str,
#     amount: float,
#     payment_type: str,
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         if payment_type not in ["paid", "collected"]:
#             raise HTTPException(status_code=400, detail="Invalid payment type")
        
#         doc_ref = firebase_db.get_document("Employees", employee_id)
#         doc = doc_ref.get()
        
#         if not doc.exists:
#             raise HTTPException(status_code=404, detail="Employee not found")
        
#         employee_data = doc.to_dict()
        
#         # Update employee
#         doc_ref.update({
#             payment_type: Increment(amount),
#             "updated_at": datetime.utcnow()
#         })
        
#         # Update counters
#         counter_ref = firebase_db.get_document("doc_counters", "employees")
#         counter_field = f"total_{payment_type}"
#         counter_ref.update({counter_field: Increment(amount)})
        
#         ActivityLogger.log_activity(
#             action="UPDATE",
#             resource="employees",
#             resource_id=employee_id,
#             user=current_user,
#             request=request,
#             details={
#                 "employee_name": employee_data.get("name"),
#                 "payment_type": payment_type,
#                 "amount": amount
#             }
#         )
        
#         return {"message": f"Employee {payment_type} updated successfully"}
#     except HTTPException:
#         raise
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="update_employee_payment",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# # ================================
# # EXPENSE ROUTES
# # ================================

# @app.get("/api/v1/expenses", response_model=List[Expense])
# async def get_expenses(
#     request: Request,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
#     category: Optional[str] = None,
#     paid_by: Optional[str] = None,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         collection_ref = firebase_db.get_collection("Expenses")
#         query = collection_ref
        
#         # Apply filters
#         if category:
#             query = query.where("category", "==", category)
#         if paid_by:
#             query = query.where("paid_by", "==", paid_by)
        
#         docs = query.order_by("created_at", direction="DESCENDING")\
#                    .offset(skip)\
#                    .limit(limit)\
#                    .stream()
        
#         expenses = [doc.to_dict() for doc in docs]
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="expenses",
#             user=current_user,
#             request=request,
#             details={"count": len(expenses), "category": category, "paid_by": paid_by}
#         )
        
#         return expenses
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="get_expenses",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/v1/expenses", response_model=Expense)
# async def create_expense(
#     expense: ExpenseCreate,
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         # Generate unique ID
#         expense_id = str(uuid.uuid4())
        
#         # Create expense data
#         expense_data = expense.dict()
#         expense_data.update({
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow()
#         })
        
#         # Save to Firebase
#         firebase_db.get_document("Expenses", expense_id).set(expense_data)
        
#         # Update counters
#         counter_ref = firebase_db.get_document("doc_counters", "expenses")
#         counter_doc = counter_ref.get()
#         if counter_doc.exists:
#             counter_ref.update({
#                 "total": Increment(1),
#                 "total_amount": Increment(expense.amount)
#             })
#         else:
#             counter_ref.set({
#                 "total": 1,
#                 "total_amount": expense.amount
#             })
        
#         # Update financial summary
#         await CounterService.update_financial_summary(current_user)
        
#         ActivityLogger.log_activity(
#             action="CREATE",
#             resource="expenses",
#             resource_id=expense_id,
#             user=current_user,
#             request=request,
#             details={
#                 "amount": expense.amount,
#                 "category": expense.category,
#                 "paid_by": expense.paid_by
#             }
#         )
        
#         return expense_data
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="create_expense",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# # ================================
# # INVENTORY ROUTES
# # ================================

# @app.get("/api/v1/inventory", response_model=List[InventoryItem])
# async def get_inventory_items(
#     request: Request,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
#     category: Optional[str] = None,
#     low_stock_only: bool = False,
#     search: Optional[str] = None,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         collection_ref = firebase_db.get_collection("Inventory Items")
        
#         # Apply category filter
#         if category:
#             docs = collection_ref.where("category", "==", category).stream()
#         else:
#             docs = collection_ref.offset(skip).limit(limit).stream()
        
#         items = []
#         for doc in docs:
#             data = doc.to_dict()
            
#             # Apply filters
#             if search and search.lower() not in data.get("name", "").lower():
#                 continue
            
#             if low_stock_only and data.get("stock_quantity", 0) > data.get("low_stock", 0):
#                 continue
            
#             items.append(data)
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="inventory",
#             user=current_user,
#             request=request,
#             details={
#                 "count": len(items),
#                 "category": category,
#                 "low_stock_only": low_stock_only,
#                 "search": search
#             }
#         )
        
#         return items
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="get_inventory_items",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/v1/inventory", response_model=InventoryItem)
# async def create_inventory_item(
#     item: InventoryItemCreate,
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         # Generate new ID
#         item_id = await CounterService.get_next_id("items", current_user)
        
#         # Create item data
#         item_data = item.dict()
#         item_data.update({
#             "id": item_id,
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow()
#         })
        
#         # Save to Firebase
#         firebase_db.get_document("Inventory Items", item_id).set(item_data)
        
#         # Update counters
#         counter_ref = firebase_db.get_document("doc_counters", "items")
#         counter_doc = counter_ref.get()
        
#         is_low_stock = item.stock_quantity <= item.low_stock
        
#         if counter_doc.exists:
#             updates = {"total": Increment(1)}
#             if is_low_stock:
#                 updates["low_stock_count"] = Increment(1)
#             counter_ref.update(updates)
#         else:
#             counter_ref.set({
#                 "total": 1,
#                 "last_id": item_id,
#                 "low_stock_count": 1 if is_low_stock else 0
#             })
        
#         ActivityLogger.log_activity(
#             action="CREATE",
#             resource="inventory",
#             resource_id=item_id,
#             user=current_user,
#             request=request,
#             details={
#                 "item_name": item.name,
#                 "category": item.category,
#                 "stock_quantity": item.stock_quantity,
#                 "is_low_stock": is_low_stock
#             }
#         )
        
#         return item_data
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="create_inventory_item",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.put("/api/v1/inventory/{item_id}/stock")
# async def update_stock(
#     item_id: str,
#     quantity: float,
#     operation: str,
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         if operation not in ["add", "subtract"]:
#             raise HTTPException(status_code=400, detail="Operation must be 'add' or 'subtract'")
        
#         doc_ref = firebase_db.get_document("Inventory Items", item_id)
#         doc = doc_ref.get()
        
#         if not doc.exists:
#             raise HTTPException(status_code=404, detail="Item not found")
        
#         old_data = doc.to_dict()
#         old_stock = old_data.get("stock_quantity", 0)
        
#         if operation == "add":
#             new_stock = old_stock + quantity
#         else:
#             new_stock = max(0, old_stock - quantity)
        
#         doc_ref.update({
#             "stock_quantity": new_stock,
#             "updated_at": datetime.utcnow()
#         })
        
#         # Update low stock counter if needed
#         old_low_stock = old_stock <= old_data.get("low_stock", 0)
#         new_low_stock = new_stock <= old_data.get("low_stock", 0)
        
#         if old_low_stock != new_low_stock:
#             counter_ref = firebase_db.get_document("doc_counters", "items")
#             if new_low_stock and not old_low_stock:
#                 counter_ref.update({"low_stock_count": Increment(1)})
#             elif not new_low_stock and old_low_stock:
#                 counter_ref.update({"low_stock_count": Increment(-1)})
        
#         ActivityLogger.log_activity(
#             action="UPDATE",
#             resource="inventory",
#             resource_id=item_id,
#             user=current_user,
#             request=request,
#             details={
#                 "item_name": old_data.get("name"),
#                 "operation": operation,
#                 "quantity_changed": quantity,
#                 "old_stock": old_stock,
#                 "new_stock": new_stock
#             }
#         )
        
#         return {"message": "Stock updated successfully", "new_quantity": new_stock}
#     except HTTPException:
#         raise
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="update_stock",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# # ================================
# # ORDER ROUTES
# # ================================

# @app.get("/api/v1/orders", response_model=List[Order])
# async def get_orders(
#     request: Request,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
#     order_type: Optional[str] = None,
#     payment_status: Optional[str] = None,
#     search: Optional[str] = None,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         collection_ref = firebase_db.get_collection("Orders")
#         query = collection_ref
        
#         # Apply filters
#         if order_type:
#             query = query.where("order_type", "==", order_type)
#         if payment_status:
#             query = query.where("payment_status", "==", payment_status)
        
#         docs = query.order_by("created_at", direction="DESCENDING")\
#                    .offset(skip)\
#                    .limit(limit)\
#                    .stream()
        
#         orders = []
#         for doc in docs:
#             data = doc.to_dict()
#             if search and search.lower() not in data.get("invoice_number", "").lower():
#                 continue
#             orders.append(data)
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="orders",
#             user=current_user,
#             request=request,
#             details={
#                 "count": len(orders),
#                 "order_type": order_type,
#                 "payment_status": payment_status,
#                 "search": search
#             }
#         )
        
#         return orders
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="get_orders",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/v1/orders", response_model=Order)
# async def create_order(
#     order: OrderCreate,
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         # Create order data
#         order_data = order.dict()
#         order_data.update({
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow(),
#             "created_by": current_user,
#             "updated_by": current_user
#         })
        
#         # Save to Firebase using invoice_number as document ID
#         firebase_db.get_document("Orders", order.invoice_number).set(order_data)
        
#         # Update inventory if it's a sell order
#         if order.order_type == "sell":
#             await update_inventory_on_sale(order.items, current_user)
        
#         # Update financial summary
#         await CounterService.update_financial_summary(current_user)
        
#         ActivityLogger.log_activity(
#             action="CREATE",
#             resource="orders",
#             resource_id=order.invoice_number,
#             user=current_user,
#             request=request,
#             details={
#                 "order_type": order.order_type,
#                 "total_amount": order.total_amount,
#                 "client_name": order.client_name,
#                 "supplier_name": order.supplier_name,
#                 "items_count": len(order.items)
#             }
#         )
        
#         return order_data
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="create_order",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.put("/api/v1/orders/{order_id}/payment-status")
# async def update_payment_status(
#     order_id: str,
#     payment_status: str,
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         doc_ref = firebase_db.get_document("Orders", order_id)
#         doc = doc_ref.get()
        
#         if not doc.exists:
#             raise HTTPException(status_code=404, detail="Order not found")
        
#         order_data = doc.to_dict()
#         old_status = order_data.get("payment_status")
        
#         doc_ref.update({
#             "payment_status": payment_status,
#             "updated_at": datetime.utcnow(),
#             "updated_by": current_user
#         })
        
#         ActivityLogger.log_activity(
#             action="UPDATE",
#             resource="orders",
#             resource_id=order_id,
#             user=current_user,
#             request=request,
#             details={
#                 "invoice_number": order_data.get("invoice_number"),
#                 "old_payment_status": old_status,
#                 "new_payment_status": payment_status
#             }
#         )
        
#         return {"message": "Payment status updated successfully"}
#     except HTTPException:
#         raise
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="update_payment_status",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# async def update_inventory_on_sale(items: List[dict], user: str = "system"):
#     """Update inventory quantities when items are sold"""
#     try:
#         for item in items:
#             item_ref = firebase_db.get_document("Inventory Items", item["item_id"])
#             item_doc = item_ref.get()
            
#             if item_doc.exists:
#                 item_data = item_doc.to_dict()
#                 new_quantity = item_data["stock_quantity"] - item["quantity"]
                
#                 # Update batches
#                 batches = item_data.get("batches", [])
#                 remaining_qty = item["quantity"]
                
#                 for batch in batches:
#                     if remaining_qty <= 0:
#                         break
#                     if batch["batch_number"] == item["batch_number"]:
#                         if batch["quantity"] >= remaining_qty:
#                             batch["quantity"] -= remaining_qty
#                             remaining_qty = 0
#                         else:
#                             remaining_qty -= batch["quantity"]
#                             batch["quantity"] = 0
                
#                 item_ref.update({
#                     "stock_quantity": new_quantity,
#                     "batches": batches,
#                     "updated_at": datetime.utcnow()
#                 })
                
#                 ActivityLogger.log_activity(
#                     action="UPDATE",
#                     resource="inventory",
#                     resource_id=item["item_id"],
#                     user=user,
#                     details={
#                         "reason": "order_sale",
#                         "item_name": item["item_name"],
#                         "quantity_sold": item["quantity"],
#                         "new_stock": new_quantity
#                     }
#                 )
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=f"Error updating inventory on sale: {str(e)}",
#             context="update_inventory_on_sale",
#             user=user,
#             exception=e
#         )

# # ================================
# # SUPPLIER ROUTES
# # ================================

# @app.get("/api/v1/suppliers", response_model=List[Supplier])
# async def get_suppliers(
#     request: Request,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
#     search: Optional[str] = None,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         collection_ref = firebase_db.get_collection("Suppliers")
        
#         if search:
#             docs = collection_ref.stream()
#             suppliers = []
#             for doc in docs:
#                 data = doc.to_dict()
#                 if search.lower() in data.get("name", "").lower():
#                     suppliers.append(data)
#         else:
#             docs = collection_ref.offset(skip).limit(limit).stream()
#             suppliers = [doc.to_dict() for doc in docs]
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="suppliers",
#             user=current_user,
#             request=request,
#             details={"count": len(suppliers), "search": search}
#         )
        
#         return suppliers
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="get_suppliers",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/v1/suppliers", response_model=Supplier)
# async def create_supplier(
#     supplier: SupplierCreate,
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         # Generate new ID
#         supplier_id = await CounterService.get_next_id("suppliers", current_user)
        
#         # Create supplier data
#         supplier_data = supplier.dict()
#         supplier_data.update({
#             "id": supplier_id,
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow()
#         })
        
#         # Save to Firebase
#         firebase_db.get_document("Suppliers", supplier_id).set(supplier_data)
        
#         ActivityLogger.log_activity(
#             action="CREATE",
#             resource="suppliers",
#             resource_id=supplier_id,
#             user=current_user,
#             request=request,
#             details={"supplier_name": supplier.name, "contact": supplier.contact}
#         )
        
#         return supplier_data
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="create_supplier",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# # ================================
# # DASHBOARD ROUTES
# # ================================

# @app.get("/api/v1/dashboard")
# async def get_dashboard_data(
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         # Get counters (optimized single read)
#         counters_ref = firebase_db.get_collection("doc_counters")
#         counters = {doc.id: doc.to_dict() for doc in counters_ref.stream()}
        
#         # Get recent orders (limited read)
#         recent_orders = firebase_db.get_collection("Orders")\
#             .order_by("created_at", direction="DESCENDING")\
#             .limit(5)\
#             .stream()
        
#         # Get low stock items (limited read)
#         low_stock_items = firebase_db.get_collection("Inventory Items")\
#             .where("stock_quantity", "<=", firebase_db.db.field_path("low_stock"))\
#             .limit(5)\
#             .stream()
        
#         dashboard_data = {
#             "financial_summary": counters.get("financial_summary", {}),
#             "counts": {
#                 "total_clients": counters.get("clients", {}).get("total", 0),
#                 "total_employees": counters.get("employees", {}).get("total", 0),
#                 "total_items": counters.get("items", {}).get("total", 0),
#                 "low_stock_count": counters.get("items", {}).get("low_stock_count", 0)
#             },
#             "recent_orders": [doc.to_dict() for doc in recent_orders][:5],
#             "low_stock_items": [doc.to_dict() for doc in low_stock_items][:5],
#             "due_payments": counters.get("clients", {}).get("total_due", 0)
#         }
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="dashboard",
#             user=current_user,
#             request=request,
#             details={"data_points": len(dashboard_data)}
#         )
        
#         return dashboard_data
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="get_dashboard_data",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# # ================================
# # REPORTS ROUTES
# # ================================

# @app.get("/api/v1/reports/sales-summary")
# async def get_sales_summary(
#     request: Request,
#     date_range: str = Query("this_month"),
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         # Parse date range
#         if start_date and end_date:
#             start = datetime.fromisoformat(start_date).date()
#             end = datetime.fromisoformat(end_date).date()
#         else:
#             # Simple date range parsing
#             today = datetime.now().date()
#             if date_range == "today":
#                 start = end = today
#             elif date_range == "this_week":
#                 start = today - timedelta(days=today.weekday())
#                 end = today
#             elif date_range == "this_month":
#                 start = today.replace(day=1)
#                 end = today
#             else:
#                 start = end = today
        
#         # Convert to datetime for Firebase query
#         start_datetime = datetime.combine(start, datetime.min.time())
#         end_datetime = datetime.combine(end, datetime.max.time())
        
#         # Get sales orders
#         orders_ref = firebase_db.get_collection("Orders")
#         docs = orders_ref.where("order_type", "==", "sell")\
#                         .where("order_date", ">=", start_datetime)\
#                         .where("order_date", "<=", end_datetime)\
#                         .stream()
        
#         total_sales = 0
#         total_orders = 0
#         payment_summary = {"paid": 0, "pending": 0, "partial": 0}
#         daily_sales = {}
        
#         for doc in docs:
#             order = doc.to_dict()
#             total_sales += order.get("total_amount", 0)
#             total_orders += 1
            
#             # Payment status summary
#             payment_status = order.get("payment_status", "pending")
#             if payment_status in payment_summary:
#                 payment_summary[payment_status] += 1
            
#             # Daily sales
#             order_date = order.get("order_date")
#             if order_date:
#                 date_key = order_date.date().isoformat()
#                 if date_key not in daily_sales:
#                     daily_sales[date_key] = 0
#                 daily_sales[date_key] += order.get("total_amount", 0)
        
#         report_data = {
#             "period": {"start": start.isoformat(), "end": end.isoformat()},
#             "total_sales": total_sales,
#             "total_orders": total_orders,
#             "average_order_value": total_sales / total_orders if total_orders > 0 else 0,
#             "payment_summary": payment_summary,
#             "daily_sales": daily_sales
#         }
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="reports",
#             user=current_user,
#             request=request,
#             details={
#                 "report_type": "sales_summary",
#                 "date_range": date_range,
#                 "total_orders": total_orders,
#                 "total_sales": total_sales
#             }
#         )
        
#         return report_data
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="get_sales_summary",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/v1/reports/inventory-report")
# async def get_inventory_report(
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         docs = firebase_db.get_collection("Inventory Items").stream()
        
#         total_items = 0
#         low_stock_items = 0
#         expired_batches = 0
#         category_summary = {}
        
#         for doc in docs:
#             item = doc.to_dict()
#             total_items += 1
            
#             # Low stock check
#             if item.get("stock_quantity", 0) <= item.get("low_stock", 0):
#                 low_stock_items += 1
            
#             # Category summary
#             category = item.get("category", "Other")
#             if category not in category_summary:
#                 category_summary[category] = {"count": 0, "total_stock": 0}
#             category_summary[category]["count"] += 1
#             category_summary[category]["total_stock"] += item.get("stock_quantity", 0)
            
#             # Check for expired batches
#             batches = item.get("batches", [])
#             for batch in batches:
#                 expiry = batch.get("Expiry", "")
#                 try:
#                     expiry_date = datetime.strptime(expiry, "%m/%Y")
#                     if expiry_date < datetime.now():
#                         expired_batches += 1
#                 except:
#                     pass
        
#         report_data = {
#             "total_items": total_items,
#             "low_stock_items": low_stock_items,
#             "expired_batches": expired_batches,
#             "category_summary": category_summary
#         }
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="reports",
#             user=current_user,
#             request=request,
#             details={
#                 "report_type": "inventory_report",
#                 "total_items": total_items,
#                 "low_stock_items": low_stock_items
#             }
#         )
        
#         return report_data
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="get_inventory_report",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# # ================================
# # ACTIVITY LOGS ROUTES
# # ================================

# @app.get("/api/v1/logs/activity")
# async def get_activity_logs(
#     request: Request,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(50, ge=1, le=500),
#     user: Optional[str] = None,
#     action: Optional[str] = None,
#     resource: Optional[str] = None,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         collection_ref = firebase_db.get_collection("activity_logs")
#         query = collection_ref
        
#         # Apply filters
#         if user:
#             query = query.where("user", "==", user)
#         if action:
#             query = query.where("action", "==", action)
#         if resource:
#             query = query.where("resource", "==", resource)
        
#         docs = query.order_by("timestamp", direction="DESCENDING")\
#                    .offset(skip)\
#                    .limit(limit)\
#                    .stream()
        
#         logs = [doc.to_dict() for doc in docs]
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="activity_logs",
#             user=current_user,
#             request=request,
#             details={"count": len(logs), "filters": {"user": user, "action": action, "resource": resource}}
#         )
        
#         return {"logs": logs, "count": len(logs)}
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="get_activity_logs",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/v1/logs/errors")
# async def get_error_logs(
#     request: Request,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(50, ge=1, le=500),
#     user: Optional[str] = None,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         collection_ref = firebase_db.get_collection("error_logs")
#         query = collection_ref
        
#         if user:
#             query = query.where("user", "==", user)
        
#         docs = query.order_by("timestamp", direction="DESCENDING")\
#                    .offset(skip)\
#                    .limit(limit)\
#                    .stream()
        
#         logs = [doc.to_dict() for doc in docs]
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="error_logs",
#             user=current_user,
#             request=request,
#             details={"count": len(logs), "user_filter": user}
#         )
        
#         return {"logs": logs, "count": len(logs)}
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="get_error_logs",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# # ================================
# # UTILITY ROUTES
# # ================================

# @app.get("/api/v1/status")
# async def api_status(
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     try:
#         # Test Firebase connection
#         test_doc = firebase_db.get_document("test", "connection").get()
        
#         status_data = {
#             "api_status": "operational",
#             "firebase_status": "connected",
#             "timestamp": datetime.utcnow().isoformat(),
#             "user": current_user
#         }
        
#         ActivityLogger.log_activity(
#             action="READ",
#             resource="system_status",
#             user=current_user,
#             request=request,
#             details=status_data
#         )
        
#         return status_data
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="api_status",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         return {
#             "api_status": "operational",
#             "firebase_status": "error",
#             "error": str(e),
#             "timestamp": datetime.utcnow().isoformat(),
#             "user": current_user
#         }

# @app.post("/api/v1/initialize")
# async def initialize_system(
#     request: Request,
#     current_user: str = Depends(get_current_user)
# ):
#     """Initialize system with default data"""
#     try:
#         await initialize_counters()
        
#         ActivityLogger.log_activity(
#             action="INITIALIZE",
#             resource="system",
#             user=current_user,
#             request=request,
#             details={"action": "system_initialization"}
#         )
        
#         return {"message": "System initialized successfully"}
#     except Exception as e:
#         ActivityLogger.log_error(
#             error=str(e),
#             context="initialize_system",
#             user=current_user,
#             request=request,
#             exception=e
#         )
#         raise HTTPException(status_code=500, detail=str(e))

# # ================================
# # MAIN APPLICATION ENTRY POINT
# # ================================

# if __name__ == "__main__":
#     import uvicorn
    
#     app_logger.info("Starting Business Management API server...")
    
#     # Log startup information
#     ActivityLogger.log_activity(
#         action="STARTUP",
#         resource="system",
#         user="system",
#         details={
#             "version": "1.0.0",
#             "firebase_credentials": settings.FIREBASE_CREDENTIALS_PATH,
#             "cors_origins": settings.CORS_ORIGINS
#         }
#     )
    
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level="info",
#         access_log=True
#     )