# MCP Key Server

A Model Context Protocol (MCP) server for securely storing API keys and providing npm package installation capabilities.

## Features

- Secure API key storage and management
- NPM package installation service
- User authentication and authorization
- Docker containerization
- AWS deployment support

## Tech Stack

- **Frontend**: React
- **Backend**: Python
- **Database**: PostgreSQL
- **Data Validation**: Pydantic
- **Containerization**: Docker
- **Cloud**: AWS

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker
- AWS CLI

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/suchetaslalom-sf/mcp-key-server.git
   cd mcp-key-server
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```

4. Start the services with Docker:
   ```bash
   docker-compose up -d
   ```

## Development

### Running Locally

#### Backend
```bash
cd backend
python app.py
```

#### Frontend
```bash
cd frontend
npm start
```

### Docker Development
```bash
docker-compose -f docker-compose.dev.yml up
```

## Deployment

### AWS Deployment
```bash
cd deployment
./deploy.sh
```

## License

MIT