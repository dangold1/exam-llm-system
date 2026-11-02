# Quick Start Guide

## TL;DR - Get Running in 5 Minutes

### Prerequisites Check

```bash
# Check if you have the required tools
node --version    # Should be v16+
python --version  # Should be 3.8+
mongosh          # Should connect (MongoDB running)
```

### 1. Setup (First Time Only)

**Backend:**

```bash
cd server
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

Create `server/.env`:

```
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=exam_system
PORT=5000
```

**Frontend:**

```bash
cd client
npm install
```

### 2. Run (Every Time)

**Terminal 1 - Backend:**

```bash
cd server
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
python app.py
```

✅ Backend running on http://localhost:5000

**Terminal 2 - Frontend:**

```bash
cd client
npm run dev
```

✅ Frontend running on http://localhost:3000


## Common Issues

**MongoDB not running?**

- Windows: Start MongoDB service from Services
- Mac: `brew services start mongodb-community`
- Linux: `sudo systemctl start mongodb`

**Port 5000 already in use?**

- Change PORT in `server/.env` to 5001
- Update `client/src/api/examApi.js` API_BASE_URL to match

**CORS errors?**

- Make sure both servers are running
- Try restarting both servers

## What's Working?

✅ Backend API serving questions  
✅ Frontend displaying 5 sample questions  
✅ Answer submission storing to MongoDB  
✅ Student ID tracking  
✅ Success/error feedback

## What's NOT Implemented (By Design)?

❌ Authentication  
❌ Viewing past submissions  
❌ Admin dashboard  
❌ Caching

