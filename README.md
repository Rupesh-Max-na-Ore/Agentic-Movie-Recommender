# 🎬 Agentic Movie Assistant

AI-powered movie recommendation and watchlist system with natural language interaction, built using LLM agents, PostgreSQL, and Docker.

---

## 🚀 Overview

Agentic Movie Assistant is a full-stack intelligent system that allows users to interact with a movie database using natural language.

It combines:

* 🤖 LLM-based agent (tool-calling)
* 🧠 Semantic recommendation engine
* 🗄️ PostgreSQL database
* 🐳 Dockerized deployment
* 🎯 Structured UI with Streamlit

---

## 🧠 System Architecture

```
User (Natural Language)
        ↓
   LLM Agent (tool selection)
        ↓
Service Layer (Python functions)
        ↓
PostgreSQL Database
        ↓
Streamlit UI (adaptive rendering)
```

---

## ✨ Features

### 🎥 Movie Discovery

* Recommend similar movies
* Semantic search (actor, genre, keywords)
* Top-rated movies (with filters)

### 📖 Movie Exploration

* Full movie details (cast, director, overview, ratings)

### 👤 User System

* Create users
* Maintain personalized state

### 📌 Watchlist Planning

* Add movies with:

  * expectations
  * natural language time (e.g., *"tomorrow at 9pm"*)

### 📋 Watchlist Management

* View planned movies
* Sorted and structured display

### ✅ Watched + Reviews

* Mark movies as watched
* Add ratings and reviews

### 📝 Custom Movie Insertion

* Add new movies with metadata

---

## 🧠 Key Concepts Demonstrated

* Agentic AI (tool-based LLM orchestration)
* Natural Language → Structured Query conversion
* Semantic retrieval using feature engineering
* Stateful user interaction system
* Schema-aware UI rendering
* Transaction-safe database operations
* Containerized multi-service architecture

---

## 🐳 Dockerized Setup (Recommended)

### 🔧 Prerequisites

* Docker Desktop installed and running

---

### ▶️ Run the App

```bash
docker compose up --build
```

---

### 🌐 Access

Open in browser:

```
http://localhost:8501
```

---

### ⚡ First Run

* Database initializes automatically
* Movie dataset loads automatically
* No manual setup required

---

## 💬 Example Commands

```
Recommend movies like Inception

Search Leonardo DiCaprio

Show top 5 horror movies with details

Give me details of Inception

Create user Rupesh

Add Inception to watchlist for Rupesh tomorrow at 9pm expecting mind blowing story

Show watchlist for Rupesh

Mark Inception as watched for Rupesh with rating 9 and review amazing
```

---

## 🗄️ Database Schema

### Movies

* title, genres, keywords, cast, director
* tags (semantic search)
* vote_average, vote_count
* overview

### Users

* username

### Planned (Watchlist)

* user, movie, expectation, watch_time

### Watched

* user, movie, rating, review

---

## 🛠️ Tech Stack

| Layer           | Technology     |
| --------------- | -------------- |
| Frontend        | Streamlit      |
| Backend         | Python         |
| AI Agent        | OpenAI API     |
| Database        | PostgreSQL     |
| DevOps          | Docker Compose |
| Data Processing | Pandas         |

---

## 📁 Project Structure

```
agentic-movie-system/
│
├── app.py                # Streamlit UI
├── agent.py              # LLM agent logic
├── services.py           # DB + business logic
├── data_processor.py     # dataset processing + DB load
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── requirements.txt
├── .env
└── README.md
```

---

## 🔒 Environment Variables

Create `.env`:

```
OPENAI_API_KEY=your_api_key
DB_NAME=moviesdb
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

---

## 🚀 Future Improvements

* Web deployment (Render / Railway)
* User authentication
* Collaborative recommendations
* Review sharing system
* Vector database integration
* UI enhancements (filters, dashboards)

---

## 📌 Resume Description

> Built a containerized AI-powered movie assistant integrating LLM-based agents with PostgreSQL and a semantic recommendation engine. Designed a full-stack system supporting natural language interaction, personalized watchlists, temporal planning, and structured retrieval using Docker Compose.

---

## 🙌 Acknowledgements

* TMDB dataset
* OpenAI API
* Streamlit

---

## ⭐ If you found this useful

Give it a star ⭐ and feel free to contribute!
