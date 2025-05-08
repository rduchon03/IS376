from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import openai

# ---------- FastAPI Setup ----------
app = FastAPI()

# ---------- CORS Setup ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- SQLite / SQLAlchemy Setup ----------
SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BookDB(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    isbn = Column(String)
    author = Column(String)
    genre = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Pydantic Models ----------
class User(BaseModel):
    Name: str
    Email: str

class Book(BaseModel):
    name: str
    isbn: str
    author: str
    genre: str

    class Config:
        orm_mode = True

class Review(BaseModel):
    Rating: int

# ---------- In-Memory Data ----------
user_list = [User(Name="Ash", Email="Ash@example.com")]
rating_list = [Review(Rating=1)]

# ---------- User Endpoints ----------
@app.get("/users")
async def get_users():
    return {"users": user_list}

@app.post("/users")
async def add_user(user: User):
    user_list.append(user)
    return {"users": user_list}

@app.delete("/users")
async def delete_user(index: int = 0):
    if index < 0 or index >= len(user_list):
        raise HTTPException(status_code=400, detail="Invalid index")
    user_list.pop(index)
    return {"users": user_list}

# ---------- Book Endpoints (Using SQLite) ----------
@app.get("/books", response_model=List[Book])
def get_books(db: Session = Depends(get_db)):
    return db.query(BookDB).all()

@app.post("/books", response_model=Book)
def add_book(book: Book, db: Session = Depends(get_db)):
    db_book = BookDB(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}", response_model=Book)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return book

# ---------- Rating Endpoints (In-Memory) ----------
@app.get("/ratings")
async def get_ratings():
    return {"ratings": rating_list}

@app.post("/ratings")
async def add_rating(review: Review):
    rating_list.append(review)
    return {"ratings": rating_list}

@app.delete("/ratings")
async def delete_rating(index: int = 0):
    if index < 0 or index >= len(rating_list):
        raise HTTPException(status_code=400, detail="Invalid index")
    rating_list.pop(index)
    return {"ratings": rating_list}

# ---------- OpenAI Suggested Rating ----------
openai.api_key = "YOUR_API_KEY"

@app.get("/suggested-rating")
async def get_suggested_rating():
    ratings = [r.Rating for r in rating_list]
    prompt = f"Based on these previous book ratings: {ratings}, what rating would you suggest for a new book?"

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"suggested_rating": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
