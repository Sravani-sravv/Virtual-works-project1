# Noteboard — Notes App

A full-stack single-page notes application with a Python/FastAPI backend and SQLite database.

## Project Structure

```
notes-app/
├── main.py           # FastAPI backend (REST API + static file serving)
├── requirements.txt  # Python dependencies
├── notes.db          # SQLite database (auto-created on first run)
└── static/
    └── index.html    # Single-page frontend
```

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the server
```bash
uvicorn main:app --reload --port 8000
```

### 3. Open in browser
```
http://localhost:8000
```

## API Endpoints

| Method | Path               | Description          |
|--------|--------------------|----------------------|
| GET    | /api/notes         | List all notes       |
| POST   | /api/notes         | Create a new note    |
| PUT    | /api/notes/{id}    | Update a note        |
| DELETE | /api/notes/{id}    | Delete a note        |

### Example Request — Create Note
```bash
curl -X POST http://localhost:8000/api/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Hello", "content": "My first note", "color": "#fef3c7"}'
```

## How It Works

1. **Frontend** (`static/index.html`) — pure HTML/CSS/JS, no framework.
   - Fetches notes from `/api/notes` on load.
   - Sends POST/PUT/DELETE requests when creating, editing, or deleting notes.
   - Updates the UI instantly from the server response.

2. **Backend** (`main.py`) — FastAPI with aiosqlite for async SQLite access.
   - Handles CRUD operations on the `notes` table.
   - Serves the frontend via `StaticFiles`.
   - Auto-creates the database and table on startup.

3. **Database** (`notes.db`) — SQLite file, zero configuration needed.
   - Schema: `id`, `title`, `content`, `color`, `created_at`, `updated_at`

## Keyboard Shortcuts
- `Ctrl+Enter` / `Cmd+Enter` — Save note
- `Escape` — Cancel editing
