# Step-by-Step Deployment Guide (Render & Vercel)

This guide walks you through hosting the **LLM-Orchestrated Cyber Threat Detection** system live.

The project consists of three main components:
1. **Database:** MySQL
2. **Backend:** FastAPI (Python 3.11)
3. **Frontend:** Vite + React + TypeScript (statically built)

---

## 🗄️ Step 1: Deploying the MySQL Database

Since the application requires a persistent MySQL database, you need to host a live MySQL database first.

### Option A: Hosting on Render (Free Tier)
1. Go to your **Render Dashboard** (<https://dashboard.render.com>).
2. Click **New** (top right) and select **PostgreSQL** or deploy a **Dockerized MySQL instance** (Render has direct support for PostgreSQL, but for MySQL, you can use a custom Docker service or use a free remote database service like Aiven/Clever Cloud).
3. **Clever Cloud / Aiven (Recommended for MySQL Free Tier):**
   - Create a free account at [Aiven.io](https://aiven.io) or [Clever-Cloud.com](https://www.clever-cloud.com).
   - Create a new **MySQL** database instance.
   - Copy the database connection URL (URI). It will look like this:
     ```text
     mysql+aiomysql://user:password@host:port/database_name
     ```
   - Store this URL safely; you will need it for the Backend deployment.
4. Run the schema migrations:
   - Connect to your remote MySQL server using any database client (e.g., DBeaver, MySQL Workbench, or CLI).
   - Run the SQL commands located inside the [backend/schema.sql](file:///d:/Major_Project/Project_8th/Project_8th/backend/schema.sql) file to create the necessary tables.

---

## 🐍 Step 2: Deploying the Backend on Render

Render is the best option for running the Python FastAPI backend, as it supports long-running web servers for free.

1. Go to your **Render Dashboard** and click **New** -> **Web Service**.
2. Connect your GitHub repository: `https://github.com/Subhash23-09/LLM-Orchestrated-Cyber-Threat-Detection`.
3. Configure the service settings:
   - **Name:** `cyber-threat-backend` (or similar)
   - **Environment:** `Python 3`
   - **Region:** Choose the region closest to you
   - **Branch:** `main`
   - **Root Directory:** `backend` (Crucial: This tells Render to compile inside the backend directory)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add the following **Environment Variables** under the "Environment" tab:

   | Key | Value | Description |
   |---|---|---|
   | `DATABASE_URL` | `mysql+aiomysql://...` | The connection string copied in Step 1 |
   | `GROQ_API_KEY` | `gsk_...` | Your Groq API key for agent orchestration |
   | `JWT_SECRET_KEY` | *[Generate a random secret]* | Generate using: `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `SECRET_KEY` | *[Generate another random secret]* | Used for system cryptographic operations |
   | `VIRUSTOTAL_API` | *[Optional VT API Key]* | Used for enriching file and IP signals |

5. Click **Create Web Service**. Render will build and deploy the backend.
6. Once deployed, Render will provide a public URL (e.g., `https://cyber-threat-backend.onrender.com`). **Copy this URL.**

---

## ⚛️ Step 3: Deploying the Frontend

You can deploy the frontend on either **Render (Static Site)** or **Vercel**. Both build static files from the `frontend/` directory.

### Option A: Deploying on Vercel (Recommended)
1. Go to the **Vercel Dashboard** (<https://vercel.com>).
2. Click **Add New** -> **Project**.
3. Import your GitHub repository: `LLM-Orchestrated-Cyber-Threat-Detection`.
4. Configure the project settings:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend` (Click edit and select the `frontend` folder)
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Expand the **Environment Variables** section and add:

   | Key | Value | Description |
   |---|---|---|
   | `VITE_API_URL` | `https://your-backend-service.onrender.com` | The URL of your Render backend from Step 2 |

6. Click **Deploy**. Vercel will install the Node dependencies, compile the TypeScript/Vite application, and host the dashboard.

---

### Option B: Deploying on Render (Static Site)
1. Go to your **Render Dashboard**, click **New** -> **Static Site**.
2. Connect your GitHub repository.
3. Configure the static site settings:
   - **Name:** `cyber-threat-frontend`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
4. Go to the **Environment** tab and add:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://your-backend-service.onrender.com` (Your Render backend URL)
5. Click **Create Static Site**.

---

## 🏁 Step 4: Verification

1. Access your frontend URL provided by Vercel or Render.
2. Sign up or log in.
3. Upload a sample security log file.
4. Verify that:
   - The files are correctly listed in the active session.
   - The Autonomous Orchestrator streams its response.
   - The database stores user credentials and incident logs.
