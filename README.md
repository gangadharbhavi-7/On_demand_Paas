# Proxmox VM Management API

This is a FastAPI-based backend application that allows you to create and manage virtual machines on a Proxmox server.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the environment variables in `.env`:
- PROXMOX_HOST: Your Proxmox server hostname or IP
- PROXMOX_USER: Proxmox username (default: root@pam)
- PROXMOX_PASSWORD: Proxmox password
- PROXMOX_VERIFY_SSL: Set to False if using self-signed certificates

## Running the Application

Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Create VM
- **POST** `/create-vm`
- Request body example:
```json
{
    "name": "my-vm",
    "vmid": 100,
    "memory": 2048,
    "cores": 2,
    "storage": "local-lvm",
    "iso": "local:iso/ubuntu-22.04.iso",
    "network": "vmbr0",
    "payment_info": {
        "upi_id": "user@upi",
        "amount": 1000.00,
        "currency": "INR",
        "payment_method": "UPI"
    }
}
```

### Get VM Status
- **GET** `/vm-status/{vmid}`
- Returns the current status of the specified VM

### Delete VM
- **DELETE** `/delete-vm/{vmid}`
- Request body example:
```json
{
    "upi_id": "user@upi",
    "amount": 500.00,
    "currency": "INR",
    "payment_method": "UPI"
}
```

## Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Payment Processing

The API uses UPI (Unified Payments Interface) for payment processing. The payment information includes:
- UPI ID (e.g., "user@upi")
- Amount
- Currency (defaults to INR)
- Payment method (UPI, UPI_QR, or UPI_INTENT)

Note: This is a demonstration implementation. In a production environment, you should:
1. Use HTTPS for all API calls
2. Integrate with a proper UPI payment gateway
3. Implement proper authentication and authorization
4. Add rate limiting and other security measures
5. Store payment information securely
6. Implement proper error handling for failed UPI transactions 