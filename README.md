# Anantha Cloud Services - VM Management Platform

A Platform-as-a-Service (PaaS) solution for managing virtual machines with integrated payment processing.

## Features

- VM Creation and Management
- UPI Payment Integration
- Real-time VM Status Monitoring
- User-friendly Web Interface

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/your-username/On_demand_Paas.git
cd On_demand_Paas
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```
PROXMOX_HOST=your_proxmox_host
PROXMOX_USER=your_proxmox_user
PROXMOX_PASSWORD=your_proxmox_password
PROXMOX_VERIFY_SSL=false
```

4. Run the development server:
```bash
python main.py
```

5. Access the application:
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

This project is configured for deployment on Vercel:

1. Push your code to GitHub
2. Import the repository in Vercel
3. Set up environment variables in Vercel dashboard
4. Deploy!

## API Endpoints

- `POST /api/create-vm` - Create a new VM
- `GET /api/vm-status/{vmid}` - Check VM status
- `DELETE /api/delete-vm/{vmid}` - Delete a VM
- `GET /api/vm-list` - List all VMs
- `GET /api/health` - Check service health

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 