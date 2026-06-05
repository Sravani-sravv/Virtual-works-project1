from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import aiosqlite
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "notes.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                color TEXT DEFAULT '#f5f0e8',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.commit()


@app.on_event("startup")
async def startup():
    await init_db()


class NoteCreate(BaseModel):
    title: str
    content: str
    color: str = "#f5f0e8"


class NoteUpdate(BaseModel):
    title: str
    content: str
    color: str


@app.get("/api/notes")
async def get_notes():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM notes ORDER BY updated_at DESC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


@app.post("/api/notes", status_code=201)
async def create_note(note: NoteCreate):
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO notes (title, content, color, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (note.title.strip(), note.content.strip(), note.color, now, now),
        )
        await db.commit()
        note_id = cursor.lastrowid
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = await cursor.fetchone()
        return dict(row)


@app.put("/api/notes/{note_id}")
async def update_note(note_id: int, note: NoteUpdate):
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Note not found")
        await db.execute(
            "UPDATE notes SET title=?, content=?, color=?, updated_at=? WHERE id=?",
            (note.title.strip(), note.content.strip(), note.color, now, note_id),
        )
        await db.commit()
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = await cursor.fetchone()
        return dict(row)


@app.delete("/api/notes/{note_id}", status_code=204)
async def delete_note(note_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Note not found")
        await db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        await db.commit()


# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")
