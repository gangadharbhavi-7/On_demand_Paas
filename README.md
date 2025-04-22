# On-Demand PaaS Application

A Platform-as-a-Service application built with FastAPI and Vercel.

## Features

- User Authentication (Signup/Login)
- Service Management
- VM Management
- Responsive UI

## Deployment Instructions

### Prerequisites

- Vercel account
- Git installed locally

### Steps to Deploy

1. Clone this repository:
   ```bash
   git clone <your-repository-url>
   cd On_demand_Paas
   ```

2. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

3. Login to Vercel:
   ```bash
   vercel login
   ```

4. Deploy the application:
   ```bash
   vercel
   ```

5. Follow the prompts to complete the deployment.

### Environment Variables

The following environment variables should be set in your Vercel project settings:

- `SECRET_KEY`: A secure random string for JWT token generation
- `DATABASE_URL`: SQLite database URL (for local development)

## Project Structure

```
On_demand_Paas/
├── frontend/
│   ├── index.html
│   ├── services.html
│   ├── style.css
│   └── script.js
├── main.py
├── requirements.txt
├── vercel.json
└── README.md
```

## Development

To run the application locally:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## License

MIT 