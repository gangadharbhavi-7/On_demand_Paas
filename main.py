from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from proxmoxer import ProxmoxAPI
import os
from dotenv import load_dotenv
import json
from typing import Optional
import time
from collections import defaultdict
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import sqlite3

# Load environment variables
load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  company TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

app = FastAPI()

# Rate limiting setup
RATE_LIMIT = 10  # requests
RATE_LIMIT_WINDOW = 60  # seconds
request_counts = defaultdict(list)

# Middleware for rate limiting
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()
    
    request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                               if now - req_time < RATE_LIMIT_WINDOW]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    
    request_counts[client_ip].append(now)
    return await call_next(request)

# Middleware for error handling
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "path": request.url.path
            }
        )

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

# Test mode flag
TEST_MODE = True  # Set to False for production

if not TEST_MODE:
    # Proxmox connection configuration
    proxmox = ProxmoxAPI(
        os.getenv('PROXMOX_HOST'),
        user=os.getenv('PROXMOX_USER'),
        password=os.getenv('PROXMOX_PASSWORD'),
        verify_ssl=os.getenv('PROXMOX_VERIFY_SSL', 'False').lower() == 'true'
    )
else:
    # Mock Proxmox for testing
    class MockProxmox:
        def __getattr__(self, name):
            return self
        def __call__(self, *args, **kwargs):
            return self
        def get(self):
            return {"status": "running"}
        def create(self, **kwargs):
            return {"status": "created"}
        def delete(self):
            return {"status": "deleted"}
        def start(self):
            return {"status": "started"}
        def stop(self):
            return {"status": "stopped"}

    proxmox = MockProxmox()

class PaymentInfo(BaseModel):
    upi_id: str
    amount: float
    currency: str = "INR"
    payment_method: str = "UPI"

class VMConfig(BaseModel):
    name: str
    vmid: int
    memory: int
    cores: int
    storage: str
    iso: str
    network: str
    payment_info: PaymentInfo

class ServiceUpdate(BaseModel):
    name: str
    description: str
    price: float
    features: list[str]

class ServiceDelete(BaseModel):
    service_id: int
    payment_info: PaymentInfo

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    company: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (token_data.email,))
    user = c.fetchone()
    conn.close()
    
    if user is None:
        raise credentials_exception
    return user

@app.get("/api")
async def read_root():
    return {"message": "Welcome to Anantha Cloud Services API"}

@app.post("/api/create-vm")
async def create_vm(vm_config: VMConfig):
    try:
        print(f"Processing UPI payment of {vm_config.payment_info.amount} {vm_config.payment_info.currency}")
        print(f"UPI ID: {vm_config.payment_info.upi_id}")
        
        vm_status = proxmox.nodes('pve').qemu.create(
            vmid=vm_config.vmid,
            name=vm_config.name,
            memory=vm_config.memory,
            cores=vm_config.cores,
            storage=vm_config.storage,
            iso=vm_config.iso,
            net0=f'virtio,bridge={vm_config.network}'
        )
        
        return {
            "status": "success",
            "message": f"VM {vm_config.name} created successfully",
            "vm_status": vm_status,
            "payment_processed": True,
            "payment_details": {
                "upi_id": vm_config.payment_info.upi_id,
                "amount": vm_config.payment_info.amount,
                "currency": vm_config.payment_info.currency
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vm-status/{vmid}")
async def get_vm_status(vmid: int):
    try:
        vm_status = proxmox.nodes('pve').qemu(vmid).status.current.get()
        return vm_status
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"VM with ID {vmid} not found")

@app.delete("/api/delete-vm/{vmid}")
async def delete_vm(vmid: int, payment_info: PaymentInfo):
    try:
        print(f"Processing deletion payment of {payment_info.amount} {payment_info.currency}")
        print(f"UPI ID: {payment_info.upi_id}")
        
        result = proxmox.nodes('pve').qemu(vmid).delete()
        
        return {
            "status": "success",
            "message": f"VM with ID {vmid} deleted successfully",
            "payment_processed": True,
            "payment_details": {
                "upi_id": payment_info.upi_id,
                "amount": payment_info.amount,
                "currency": payment_info.currency
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    try:
        proxmox.nodes.get()
        return {"status": "healthy", "message": "Service is running normally"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="Service unavailable: Could not connect to Proxmox"
        )

@app.get("/api/vm-list")
async def get_vm_list():
    try:
        # In test mode, return mock data
        if TEST_MODE:
            return [
                {"name": "Test VM 1", "vmid": 100, "status": "running"},
                {"name": "Test VM 2", "vmid": 101, "status": "stopped"}
            ]
        
        # In production, get actual VM list from Proxmox
        vms = proxmox.nodes('pve').qemu.get()
        return [
            {
                "name": vm.get('name', f"VM {vm['vmid']}"),
                "vmid": vm['vmid'],
                "status": vm.get('status', 'unknown')
            }
            for vm in vms
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/update-service/{service_id}")
async def update_service(service_id: int, service_update: ServiceUpdate):
    try:
        # In test mode, return mock response
        if TEST_MODE:
            return {
                "status": "success",
                "message": f"Service {service_id} updated successfully",
                "service": {
                    "id": service_id,
                    "name": service_update.name,
                    "description": service_update.description,
                    "price": service_update.price,
                    "features": service_update.features
                }
            }
        
        # In production, update the service in the database
        # This is a placeholder - replace with your actual database update logic
        updated_service = {
            "id": service_id,
            "name": service_update.name,
            "description": service_update.description,
            "price": service_update.price,
            "features": service_update.features
        }
        
        return {
            "status": "success",
            "message": f"Service {service_id} updated successfully",
            "service": updated_service
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/delete-service/{service_id}")
async def delete_service(service_id: int, service_delete: ServiceDelete):
    try:
        print(f"Processing deletion payment of {service_delete.payment_info.amount} {service_delete.payment_info.currency}")
        print(f"UPI ID: {service_delete.payment_info.upi_id}")
        
        # In test mode, return mock response
        if TEST_MODE:
            return {
                "status": "success",
                "message": f"Service {service_id} deleted successfully",
                "payment_processed": True,
                "payment_details": {
                    "upi_id": service_delete.payment_info.upi_id,
                    "amount": service_delete.payment_info.amount,
                    "currency": service_delete.payment_info.currency
                }
            }
        
        # In production, delete the service from the database
        # This is a placeholder - replace with your actual database deletion logic
        
        return {
            "status": "success",
            "message": f"Service {service_id} deleted successfully",
            "payment_processed": True,
            "payment_details": {
                "upi_id": service_delete.payment_info.upi_id,
                "amount": service_delete.payment_info.amount,
                "currency": service_delete.payment_info.currency
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/signup", response_model=Token)
async def signup(user: UserSignup):
    try:
        # Check if user already exists
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (user.email,))
        existing_user = c.fetchone()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = get_password_hash(user.password)
        c.execute(
            "INSERT INTO users (name, email, password, company) VALUES (?, ?, ?, ?)",
            (user.name, user.email, hashed_password, user.company)
        )
        conn.commit()
        conn.close()
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (form_data.username,))
        user = c.fetchone()
        conn.close()
        
        if not user or not verify_password(form_data.password, user[3]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user[2]}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/users/me")
async def read_users_me(current_user: tuple = Depends(get_current_user)):
    return {
        "id": current_user[0],
        "name": current_user[1],
        "email": current_user[2],
        "company": current_user[4]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

