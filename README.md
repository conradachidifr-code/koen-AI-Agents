<<<<<<< HEAD
# koen-AI-Agents
Conrad's Custom AI Agents 
=======
# DBuddy

Your friendly database buddy! A natural language chatbot that converts plain English questions into SQL queries, executes them against your MySQL database, and returns human-readable answers using a local LLM via Ollama.

## Features

- **Natural Language Processing**: Ask questions in plain English
- **Text-to-SQL Conversion**: Automatically converts questions to SQL queries using local AI
- **Human-Readable Responses**: Results are formatted in conversational language
- **Web Interface**: Clean, modern chat UI
- **Safety Features**: Blocks destructive SQL operations (DROP, DELETE, UPDATE, etc.)
- **Schema-Aware**: Automatically learns your database structure
- **Minikube Support**: Designed to work with MySQL running on Minikube
- **100% Local & Private**: Runs entirely on your machine with Ollama - no API costs!

## Architecture

```
User Question → Ollama LLM (Text-to-SQL) → MySQL Database → Results → Ollama LLM (Formatting) → User Answer
```

## Prerequisites

- Python 3.8+
- Ollama installed and running locally
- MySQL database running on Minikube
- kubectl configured for your Minikube cluster

## Setup

### 1. Install Ollama

First, install Ollama on your system:

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Or download from:** https://ollama.com/download

**Start Ollama:**
```bash
ollama serve
```

**Pull a model (choose one):**
```bash
# Recommended: Mistral (good balance of speed and quality for SQL)
ollama pull mistral

# Or Llama2 (lighter, faster)
ollama pull llama2

# Or CodeLlama (optimized for code, including SQL)
ollama pull codellama

# Or Llama3 (newer, more capable)
ollama pull llama3
```

### 2. Clone and Navigate

```bash
cd /path/to/your/DBuddy
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Minikube MySQL Connection

First, you need to expose your MySQL service from Minikube. Choose one of these methods:

#### Option A: Port Forwarding (Recommended)

```bash
# Find your MySQL service
kubectl get svc -A | grep mysql

# Port forward (replace <namespace> and <service-name> with your values)
kubectl port-forward -n <namespace> svc/<mysql-service-name> 3306:3306
```

This will forward local port 3306 to your MySQL service in Minikube.

#### Option B: NodePort

```bash
# Get the URL (replace <namespace> and <service-name>)
minikube service -n <namespace> <mysql-service-name> --url
```

Use the returned host and port in your configuration.

#### Helper Script

Run the included helper script for connection details:

```bash
./get_minikube_mysql.sh
```

### 6. Get MySQL Credentials

If you don't know your MySQL password:

```bash
# Get password from Kubernetes secret (replace <namespace> and <secret-name>)
kubectl get secret -n <namespace> <mysql-secret-name> -o jsonpath='{.data.mysql-root-password}' | base64 -d
echo
```

### 7. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

Update the `.env` file:

```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral  # or llama2, codellama, llama3, etc.

# MySQL Database Configuration
MYSQL_HOST=localhost  # or 127.0.0.1
MYSQL_PORT=3306      # or the NodePort if using that method
MYSQL_USER=root
MYSQL_PASSWORD=your_actual_password
MYSQL_DATABASE=your_database_name
```

**Note:** The `OLLAMA_MODEL` should match the model you pulled in step 1. Recommended models:
- `mistral` - Best balance of speed and quality
- `codellama` - Optimized for SQL generation
- `llama2` - Lightweight and fast
- `llama3` - More capable, newer model

### 8. Test Database Connection

```bash
# Test connection using kubectl
kubectl exec -it -n <namespace> <mysql-pod-name> -- mysql -u root -p

# Or use Python to test the connection
python -c "from database import db_manager; print('Connected!' if db_manager.test_connection() else 'Failed!')"
```

## Running the Application

### Start the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Access the Web UI

Open your browser and navigate to:

```
http://localhost:8000
```

## Usage Examples

Once the web interface is open, you can ask questions like:

- "Show me all users"
- "How many orders were placed last month?"
- "What are the top 5 products by revenue?"
- "List customers from California"
- "What's the average order value?"
- "Show me the most recent 10 transactions"

The chatbot will:
1. Convert your question to SQL
2. Execute it against your database
3. Show you the SQL query that was generated
4. Return the results in plain English

## API Endpoints

### `GET /`
Serves the web chat interface

### `GET /health`
Health check endpoint
- Returns database connection status

### `POST /api/query`
Process a natural language query

**Request:**
```json
{
  "query": "How many users do we have?"
}
```

**Response:**
```json
{
  "success": true,
  "response": "You have 1,234 users in the database.",
  "sql_query": "SELECT COUNT(*) as count FROM users;"
}
```

### `GET /api/schema`
Get the database schema

**Response:**
```json
{
  "success": true,
  "schema": "Table: users\n  - id (int) PRIMARY KEY\n  - name (varchar(255))\n  ..."
}
```

## Project Structure

```
.
├── main.py              # FastAPI application
├── agent.py             # Ollama-powered SQL agent
├── database.py          # MySQL database manager
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Environment variables template
├── get_minikube_mysql.sh # Helper script for Minikube MySQL
├── static/
│   ├── index.html       # Web UI
│   ├── style.css        # Styles
│   └── script.js        # Frontend JavaScript
└── README.md            # This file
```

## Security Features

- **Read-Only Queries**: Only SELECT queries are allowed
- **SQL Injection Protection**: Uses parameterized queries via PyMySQL
- **Dangerous Operations Blocked**: DROP, DELETE, UPDATE, INSERT, ALTER, etc. are rejected
- **Input Validation**: All user inputs are validated

## Troubleshooting

### Database Connection Failed

1. Ensure Minikube is running:
   ```bash
   minikube status
   ```

2. Verify port forwarding is active:
   ```bash
   lsof -i :3306
   ```

3. Test MySQL connection directly:
   ```bash
   mysql -h 127.0.0.1 -P 3306 -u root -p
   ```

### Ollama Connection Errors

1. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

2. Verify the model is downloaded:
   ```bash
   ollama list
   ```

3. Test Ollama directly:
   ```bash
   ollama run mistral "SELECT * FROM users"
   ```

4. Check Ollama host in `.env` is correct (default: `http://localhost:11434`)

### Web UI Not Loading

1. Ensure the server is running on port 8000
2. Check that the `static` directory exists with all files
3. Look for errors in the server logs

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload
```

### Running Tests

```bash
# Test database connection
python -c "from database import db_manager; print(db_manager.get_schema())"

# Test Ollama integration
python -c "from agent import agent; print(agent.process_query('How many tables are there?'))"
```

## License

MIT

## Contributing

Feel free to open issues or submit pull requests!
>>>>>>> 26bbb23 (Initial commit)
