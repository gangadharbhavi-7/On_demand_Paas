from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
from pathlib import Path

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Templates
templates = Jinja2Templates(directory="frontend")

# Models
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

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/services", response_class=HTMLResponse)
async def read_services(request: Request):
    return templates.TemplateResponse("services.html", {"request": request})

@app.post("/api/create-vm")
async def create_vm(vm_config: VMConfig):
    try:
        print(f"Processing UPI payment of {vm_config.payment_info.amount} {vm_config.payment_info.currency}")
        print(f"UPI ID: {vm_config.payment_info.upi_id}")
        
        # Mock VM creation
        vm_status = {
            "status": "created",
            "vmid": vm_config.vmid,
            "name": vm_config.name
        }
        
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
        # Mock VM status
        return {
            "status": "running",
            "vmid": vmid,
            "uptime": "1h 30m"
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"VM with ID {vmid} not found")

@app.delete("/api/delete-vm/{vmid}")
async def delete_vm(vmid: int, payment_info: PaymentInfo):
    try:
        print(f"Processing deletion payment of {payment_info.amount} {payment_info.currency}")
        print(f"UPI ID: {payment_info.upi_id}")
        
        # Mock VM deletion
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
    return {"status": "healthy", "message": "Service is running normally"}

@app.get("/api/vm-list")
async def get_vm_list():
    try:
        # Mock VM list
        return [
            {"name": "Test VM 1", "vmid": 100, "status": "running"},
            {"name": "Test VM 2", "vmid": 101, "status": "stopped"}
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/update-service/{service_id}")
async def update_service(service_id: int, service_update: ServiceUpdate):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/delete-service/{service_id}")
async def delete_service(service_id: int, service_delete: ServiceDelete):
    try:
        print(f"Processing deletion payment of {service_delete.payment_info.amount} {service_delete.payment_info.currency}")
        print(f"UPI ID: {service_delete.payment_info.upi_id}")
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

