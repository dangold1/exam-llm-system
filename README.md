# Exam System

A minimal full-stack application for managing and submitting open-ended exam questions. This project serves as a foundation for a live interview.

## Features

- **Backend Options**
  - **Python Flask** (`python/server/`) - Flask + MongoDB
  - **Node.js Express** (`nodejs/server/`) - Express + MongoDB
  - Fetch exam questions from MongoDB
  - Submit student answers
- **Frontend (React + Vite)**
  - Display exam questions
  - Text input for answers
  - Submit all answers with student ID

## Tech Stack

- **Frontend**: React 18, Vite, Axios
- **Backend Options**:
  - **Python**: Python 3, Flask, PyMongo
  - **Node.js**: Node.js 16+, Express, MongoDB Driver
- **Database**: MongoDB **(local instance)**

## Project Structure

```
exam-system/
├── python/
│   ├── client/                 # React frontend (Python version)
│   │   ├── src/
│   │   │   ├── api/           # API integration
│   │   │   ├── components/    # React components
│   │   │   ├── pages/         # Page components
│   │   │   └── styles/        # CSS files
│   │   ├── index.html
│   │   ├── package.json
│   │   └── vite.config.js
│   └── server/                # Flask backend
│       ├── db/
│       │   └── database.py    # MongoDB connection & initialization
│       ├── routes/
│       │   ├── questions.py   # GET /questions endpoint
│       │   └── submissions.py # POST /submit endpoint
│       ├── app.py             # Flask app entry point
│       └── requirements.txt
├── nodejs/
│   ├── client/                 # React frontend (Node.js version)
│   │   ├── src/
│   │   │   ├── api/           # API integration
│   │   │   ├── components/    # React components
│   │   │   ├── pages/         # Page components
│   │   │   └── styles/        # CSS files
│   │   ├── index.html
│   │   ├── package.json
│   │   └── vite.config.js
│   └── server/                # Express backend
│       ├── db/
│       │   └── database.js    # MongoDB connection & initialization
│       ├── routes/
│       │   ├── questions.js   # GET /questions endpoint
│       │   └── submissions.js # POST /submit endpoint
│       ├── app.js             # Express app entry point
│       └── package.json
└── README.md
```

## Prerequisites

Before running this project, make sure you have installed:

- **Node.js** (v16 or higher) and npm
- **Python** (v3.8 or higher) and pip (if using Python backend)
- **MongoDB** (v4.4 or higher)

### Installing MongoDB

**Windows:**

1. Download MongoDB Community Server from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Run the installer and follow the setup wizard
3. MongoDB will start automatically as a Windows service

**macOS (using Homebrew):**

```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

Verify MongoDB is running:

```bash
# Should connect without errors
mongosh
```

## Setup Instructions

### Choose Your Backend Stack

This project supports two backend implementations:

- **Python Flask** (`python/server/`) - Recommended for Python developers
- **Node.js Express** (`nodejs/server/`) - Recommended for JavaScript/Node.js developers

Both backends provide the same API endpoints and functionality. Choose the one that best fits your development environment.

---

## Option 1: Python Flask Backend

### 1. Backend Setup

```bash
# Navigate to Python server directory
cd python/server

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
```

Create a `python/server/.env` file with:

```env
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=exam_system
PORT=5000
```

For Azure OpenAI grading, add the `AZURE_OPENAI_*` variables described in `CLAUDE.md`. **Grades are not guaranteed identical on every run** for the same text (LLM sampling). Optional **`GRADING_SEED`** in `.env` can improve repeatability when your deployment supports the API `seed` parameter.

### 2. Frontend Setup

```bash
# Navigate to Python client directory (from project root)
cd python/client

# Install dependencies
npm install
```

### 3. Running the Application

**Terminal 1 - Backend:**

```bash
cd python/server
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
python app.py
```

✅ Backend running on http://localhost:5000

**Terminal 2 - Frontend:**

```bash
cd python/client
npm run dev
```

✅ Frontend running on http://localhost:3000

---

## Option 2: Node.js Express Backend

### 1. Backend Setup

```bash
# Navigate to Node.js server directory
cd nodejs/server

# Install dependencies
npm install

# Create .env file
```

Create a `nodejs/server/.env` file with:

```env
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=exam_system
PORT=5000
```

### 2. Frontend Setup

```bash
# Navigate to Node.js client directory (from project root)
cd nodejs/client

# Install dependencies
npm install
```

### 3. Running the Application

**Terminal 1 - Backend:**

```bash
cd nodejs/server
npm start
# Or for development with auto-reload:
npm run dev
```

✅ Backend running on http://localhost:5000

**Terminal 2 - Frontend:**

```bash
cd nodejs/client
npm run dev
```

✅ Frontend running on http://localhost:3000

---

## Access the Application

Open your browser and navigate to:

```
http://localhost:3000
```

## Usage

1. **Enter Student ID**: Type your student ID in the input field
2. **Answer Questions**: Each question has a text area for your answer
3. **Submit**: Click "Submit Exam" to submit all answers
4. **Confirmation**: A success message will appear upon successful submission

## Troubleshooting

### MongoDB Connection Issues

**Error: "Connection refused"**

- Ensure MongoDB is running: `mongosh`
- Check if MongoDB is on the default port: 27017
- Verify `.env` file has correct `MONGODB_URI`

### Port Already in Use

**Backend (Port 5000):**

- Change `PORT` in `server/.env`
- Update `API_BASE_URL` in `client/src/api/examApi.js`

**Frontend (Port 3000):**

- Vite will automatically suggest another port
- Or change port in `client/vite.config.js`

### CORS Issues

Both backends have CORS enabled for all origins. If you encounter CORS errors:

- Ensure both frontend and backend are running
- Check browser console for specific error messages

### Python Dependencies (Flask Backend)

If you encounter import errors:

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Node.js Dependencies (Express Backend)

If you encounter module errors:

```bash
cd nodejs/server
rm -rf node_modules package-lock.json
npm install
```

## Development Notes

- Both backends automatically initialize sample questions on first run
- Submissions are stored with timestamps for future reference
- No authentication is required (suitable for local development)
- Both implementations use the same MongoDB database (`exam_system`)
- The client-side code is identical for both versions

## Quick Start Comparison

| Task           | Python Flask                                          | Node.js Express                   |
| -------------- | ----------------------------------------------------- | --------------------------------- |
| Backend Setup  | `cd python/server && pip install -r requirements.txt` | `cd nodejs/server && npm install` |
| Frontend Setup | `cd python/client && npm install`                     | `cd nodejs/client && npm install` |
| Run Backend    | `python app.py`                                       | `npm start`                       |
| Run Frontend   | `npm run dev`                                         | `npm run dev`                     |
| Ports          | Backend: 5000, Frontend: 3000                         | Backend: 5000, Frontend: 3000     |
