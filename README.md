# Banking App

A minimalistic banking application built with FastAPI (backend) and React + Tailwind CSS (frontend).

## Features

- **User Authentication**: JWT-based authentication with password hashing (bcrypt)
- **Account Management**: Create and manage multiple bank accounts
- **Transactions**: Deposit, withdraw, and transfer money between accounts
- **Bill Payments**: Track and pay bills from your accounts

## Tech Stack

### Backend
- FastAPI (Python)
- MongoDB (Motor async driver)
- JWT Authentication (python-jose)
- Password Hashing (passlib + bcrypt)

### Frontend
- React 18
- React Router v6
- Tailwind CSS
- Axios
- Vite

## Project Structure

```
├── backend/
│   ├── routes/
│   │   ├── auth.py          # Authentication routes
│   │   ├── accounts.py      # Account management
│   │   ├── transactions.py  # Transaction handling
│   │   └── bills.py         # Bill management
│   ├── main.py              # FastAPI app entry
│   ├── models.py            # Pydantic models
│   ├── database.py          # MongoDB connection
│   ├── auth.py              # JWT utilities
│   ├── requirements.txt
│   └── render.yaml          # Render deployment config
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── context/         # Auth context
│   │   ├── services/        # API service
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── vercel.json          # Vercel deployment config
└── README.md
```

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (or local MongoDB)

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file with your MongoDB URI:
   ```
   MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/Bankingapp
   SECRET_KEY=your-super-secret-key-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

## Deployment

### Backend on Render

1. Create a new **Web Service** on [Render](https://render.com)

2. Connect your GitHub repository and select the `backend` folder as root directory

3. Configure the service:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. Add environment variables in Render dashboard:
   - `MONGODB_URI` - Your MongoDB connection string
   - `SECRET_KEY` - A secure random string for JWT
   - `ALGORITHM` - `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` - `30`

5. Deploy and copy your backend URL (e.g., `https://banking-api.onrender.com`)

### Frontend on Vercel

1. Create a new project on [Vercel](https://vercel.com)

2. Connect your GitHub repository and select the `frontend` folder as root directory

3. Configure build settings (should auto-detect Vite):
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. Add environment variable:
   - `VITE_API_URL` - Your Render backend URL (e.g., `https://banking-api.onrender.com`)

5. Deploy!

### Important Notes

- Make sure CORS is properly configured in the backend for your Vercel domain
- Update the backend's CORS settings in `main.py` if needed to include your production frontend URL

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (form data)
- `POST /api/auth/login/json` - Login (JSON body)

### User
- `GET /api/me` - Get current user info

### Accounts
- `GET /api/accounts` - List user's accounts
- `POST /api/accounts` - Create new account
- `GET /api/accounts/{id}` - Get account details

### Transactions
- `GET /api/transactions/{account_id}` - List transactions
- `POST /api/transactions/{account_id}` - Create transaction

### Bills
- `GET /api/bills` - List user's bills
- `POST /api/bills` - Add new bill
- `POST /api/bills/pay` - Pay a bill
- `DELETE /api/bills/{id}` - Delete a bill

## Security Notes

- Passwords are hashed using bcrypt
- JWT tokens expire after 30 minutes (configurable)
- All sensitive routes require authentication
- CORS is configured for frontend origins

## License

MIT
