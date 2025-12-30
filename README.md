# CineVibe - Mood-Based Movie Recommender 🎬✨

CineVibe is a full-stack web application that suggests movies based on your current mood using **Groq AI (Llama-3)** and **Supabase**. It dynamically generates movie data if a specific genre or vibe is missing from the database.

---

## 🚀 Features
- **AI-Powered Vibe Matching**: Understands natural language (e.g., "I want a dark sci-fi with a hopeful ending").
- **Dynamic Seeding**: Automatically populates the database with new movies if matches are scarce.
- **Modern UI**: Built with React, Tailwind CSS, and Framer Motion.
- **Full Auth**: User authentication via Supabase.

---

## 🛠 Prerequisites
- **Node.js** (v16 or higher)
- **Python** (v3.9 or higher)
- **Supabase Account** (for Database & Auth)
- **Groq API Key** (for AI logic)

---

## 📥 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/SaiBadam06/CineVibe.git
cd CineVibe
```

---

### 2. Backend Setup (FastAPI)

Navigate to the backend folder:
```bash
cd backend
```

Create a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

**Configure Environment Variables:**
Create a `.env` file in the `backend` folder:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GROQ_API_KEY=your_groq_api_key
```

**Run the Backend:**
```bash
python -m uvicorn main:app --reload
```
*The backend will start at `http://127.0.0.1:8000`*

---

### 3. Frontend Setup (React + Vite)

Open a new terminal and navigate to the frontend folder:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

**Configure Environment Variables:**
Create a `.env` file in the `frontend` folder:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
# Optional: Defaults to localhost. Change only for production.
# VITE_API_URL=https://your-backend-url.onrender.com 
```

**Run the Frontend:**
```bash
npm run dev
```
*The frontend will start at `http://localhost:5173` (or similar)*

---

## 🗄️ Database Setup (Supabase)

1.  Go to your [Supabase Dashboard](https://supabase.com/dashboard).
2.  Open the **SQL Editor**.
3.  Copy the contents of `backend/schema.sql` and run it to create the tables.
4.  **(Optional)** To populate initial data, run the `backend/seed.py` script:
    ```bash
    cd backend
    python seed.py
    ```

---

## 🧪 Usage
1.  Open the frontend URL (e.g., `http://localhost:5173`).
2.  Log in or sign up.
3.  Navigate to the "Explore" or "Vibe" page.
4.  Type your mood (e.g., "Suspenseful thriller") to see recommendations!

---

## 📄 License
This project is for educational purposes. All movie data is generated/mocked or sourced from public datasets.
