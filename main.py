from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from proxmoxer import ProxmoxAPI
import os
from dotenv import load_dotenv
import json
from typing import Optional
import time
from collections import defaultdict

# Load environment variables
load_dotenv()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

