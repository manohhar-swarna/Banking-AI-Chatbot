# 🏦 AI Agent Chatbot for Banking Domain

An intelligent **AI Agent–based Chatbot** designed for the **banking domain**, built using **LangChain agents**, **OpenAI LLMs**, **SQL**, and **external APIs**.  
The chatbot simulates realistic banking conversations, handles structured and unstructured data, performs SQL-based reasoning, integrates external APIs, and maintains contextual memory with controlled privacy.

---

## 📌 Project Description

This project implements an **AI Agent Chatbot** that behaves like a banking virtual assistant.  
It supports **natural conversations**, **user onboarding**, **account-related queries**, **database lookups**, **CSV-based data access**, **story retrieval**, **web search**, and **external API calls**, while maintaining **conversation history** and **data privacy rules**.

The chatbot is built using **LangChain’s agent framework**, enabling the LLM to dynamically select tools such as SQL queries, CSV readers, file-based retrieval, external APIs, and free web search.

---

## 🛠️ Tech Stack

### Languages
- **Python** (managed using `uv`)
- **SQL** (SQLite)

### Frameworks & Libraries
- **LangChain** (Agents & Tools)
- **OpenAI** (`ChatOpenAI`)
- **Pydantic** (Schema validation)
- **SQLite3** (Persistent storage)
- **Pandas** (CSV processing)
- **python-dotenv** (Environment variables)

### APIs
- **OpenAI API**
- **RapidAPI**

---

## ✨ Features

### 1. User Greeting & Onboarding
- Displays a welcome message
- Asks for the user’s name
- Generates a unique greeting if the user says *“no”*
- Greets the user personally if a name is provided

---

### 2. Banking Balance Simulation
- Responds to balance-check queries
- Generates a **dynamic fake balance** each time
- Uses professional banking terminology

---

### 3. Exit Handling & Session Closure
- Recognizes `quit` or `exit`
- Sends a unique goodbye message
- Gracefully terminates the application

---

### 4. Conversation Persistence
- Saves full conversations to the `conversation/` folder on exit
- Each conversation file has a **unique filename**
- Every message is also stored in a database

---

### 5. Context-Aware Memory
- Only the **latest 10 conversations** are sent to the LLM
- Improves response relevance and controls token usage

---

### 6. Free Web Search Tool
- Enables the agent to fetch external information dynamically

---

### 7. SQL-Based Employee Data Access
- SQLite `employees` table with a `private` (boolean) column
- If `private = true`, the LLM responds with *“This is a private record”*
- If `private = false`, employee data is displayed
- Employee-related queries trigger SQL execution automatically

---

### 8. CSV-Based User Data Retrieval
- Reads from `user.csv`
- LLM can fetch and analyze user details directly

---

### 9. External API Integration
- Uses RapidAPI for external data sources
- Tool-based API invocation by the LLM

---

### 10. Story Retrieval System
- `stories/1.txt` and `stories/2.txt`
- Returns story content based on user request

---
## ⚙️ Setup Instructions

Follow the steps below to set up and run the **Banking AI Chatbot** application locally.

---

### 1️⃣ Clone the GitHub Repository

```bash
git clone https://github.com/manohhar-swarna/Banking-AI-Chatbot.git
cd Banking-AI-Chatbot
```
---

### 2️⃣ Install `uv` (Python Package Manager)

`uv` is used to manage Python versions and project dependencies.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### 3️⃣ Add `uv` to Your PATH

```bash
export PATH="$HOME/.local/bin:$PATH"
```

This ensures the `uv` command is available globally in your terminal.

---

### 4️⃣ Verify `uv` Installation

```bash
uv
```

If installed correctly, this command will display the `uv` help output.

---

### 5️⃣ Install Project Dependencies

```bash
uv sync
```

This command installs all required dependencies for the project.

---

### 6️⃣ Configure Environment Variables

Create a `.env` file in the project root directory and add the following:

```env
OPENAI_API_KEY=your_openai_api_key
RAPID_API_KEY=your_rapid_api_key
```

> 🔐 **Important:** Do not commit the `.env` file to GitHub.

---

### 7️⃣ Database Setup

#### Create Employee Database and Table

```bash
uv src/employee_database.py
```

This initializes the `employees` table with required schema and sample data.

---

#### Create Chatbot Conversation Database and Table

```bash
uv src/chatbot_conversation_database.py
```

This creates the database and table used to store chatbot conversation history.

---

### 8️⃣ Run the Chatbot Application

```bash
uv run src/chatbot.py
```

The AI Banking Chatbot will now start running in the terminal.

---



