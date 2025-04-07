from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from proxmoxer import ProxmoxAPI
import os
from dotenv import load_dotenv
import json
from typing import Optional

# Load environment variables
load_dotenv()

app = FastAPI()

# Proxmox connection configuration
proxmox = ProxmoxAPI(
    os.getenv('PROXMOX_HOST'),
    user=os.getenv('PROXMOX_USER'),
    password=os.getenv('PROXMOX_PASSWORD'),
    verify_ssl=os.getenv('PROXMOX_VERIFY_SSL', 'False').lower() == 'true'
)

class PaymentInfo(BaseModel):
    upi_id: str
    amount: float
    currency: str = "INR"
    payment_method: str = "UPI"  # Can be "UPI", "UPI_QR", "UPI_INTENT"

class VMConfig(BaseModel):
    name: str
    vmid: int
    memory: int
    cores: int
    storage: str
    iso: str
    network: str
    payment_info: PaymentInfo

@app.post("/create-vm")
async def create_vm(vm_config: VMConfig):
    try:
        # Here you would typically process the UPI payment first
        # For demonstration, we'll just log the payment info
        print(f"Processing UPI payment of {vm_config.payment_info.amount} {vm_config.payment_info.currency}")
        print(f"UPI ID: {vm_config.payment_info.upi_id}")
        
        # Create the VM
        proxmox.nodes('pve').qemu.create(
            vmid=vm_config.vmid,
            name=vm_config.name,
            memory=vm_config.memory,
            cores=vm_config.cores,
            storage=vm_config.storage,
            iso=vm_config.iso,
            net0=f'virtio,bridge={vm_config.network}'
        )
        
        # Start the VM
        proxmox.nodes('pve').qemu(vm_config.vmid).status.start.post()
        
        # Get VM status
        vm_status = proxmox.nodes('pve').qemu(vm_config.vmid).status.current.get()
        
        return {
            "status": "success",
            "message": f"VM {vm_config.name} created and started successfully",
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

@app.get("/vm-status/{vmid}")
async def get_vm_status(vmid: int):
    try:
        vm_status = proxmox.nodes('pve').qemu(vmid).status.current.get()
        return vm_status
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"VM with ID {vmid} not found")

@app.delete("/delete-vm/{vmid}")
async def delete_vm(vmid: int, payment_info: PaymentInfo):
    try:
        # Process payment for deletion (if applicable)
        print(f"Processing deletion payment of {payment_info.amount} {payment_info.currency}")
        print(f"UPI ID: {payment_info.upi_id}")
        
        # Stop the VM if it's running
        try:
            proxmox.nodes('pve').qemu(vmid).status.stop.post()
        except:
            pass  # VM might already be stopped
        
        # Delete the VM
        proxmox.nodes('pve').qemu(vmid).delete()
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 