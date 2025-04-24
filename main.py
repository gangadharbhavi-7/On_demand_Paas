from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
import os
import socket
from pathlib import Path
from fastapi import status

# Load environment variables
PORT = int(os.getenv("PORT", "8001"))
HOST = os.getenv("HOST", "0.0.0.0")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port):
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

app = FastAPI(debug=DEBUG)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path("frontend")
if not static_dir.exists():
    static_dir.mkdir(parents=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Templates
templates_dir = Path("frontend")
if not templates_dir.exists():
    templates_dir.mkdir(parents=True)
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

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

# Get the absolute path to the frontend directory
frontend_dir = Path(__file__).parent / "frontend"

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return FileResponse(frontend_dir / "index.html")

@app.get("/services", response_class=HTMLResponse)
async def read_services(request: Request):
    return FileResponse(frontend_dir / "services.html")

@app.get("/contact", response_class=HTMLResponse)
async def read_contact(request: Request):
    return FileResponse(frontend_dir / "contact.html")

@app.get("/about", response_class=HTMLResponse)
async def read_about(request: Request):
    return FileResponse(frontend_dir / "about.html")

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
    return {
        "status": "healthy",
        "message": "Service is running normally",
        "environment": ENVIRONMENT,
        "debug": DEBUG
    }

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

@app.post("/api/contact")
async def submit_contact_form(contact_form: ContactForm):
    """
    Handle contact form submissions.
    In a production environment, this would typically:
    1. Save the message to a database
    2. Send an email notification
    3. Set up an auto-responder
    """
    try:
        # For now, we'll just validate and return success
        # In production, implement email sending and database storage
        return {
            "status": "success",
            "message": "Thank you for your message! We will get back to you soon."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process contact form submission"
        )

if __name__ == "__main__":
    import uvicorn
    try:
        # Check if the port is available
        if is_port_in_use(8001):
            print(f"Port 8001 is in use. Trying to find an available port...")
            PORT = find_available_port(8001)
            print(f"Found available port: {PORT}")
        else:
            PORT = 8001

        print(f"Server will run on 0.0.0.0:{PORT}")
        uvicorn.run(app, host="0.0.0.0", port=PORT)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        print("Please check if another process is using the port or if you have the necessary permissions.")

