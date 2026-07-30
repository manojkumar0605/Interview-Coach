from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, run_migrations
from app.routers import auth, resume, session, progress

# Create database tables & run column migrations
Base.metadata.create_all(bind=engine)
run_migrations()

app = FastAPI(
    title="AI Interview Coach API",
    description="Backend service for AI Interview Coach powered by OpenRouter",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3005",
        "http://localhost:3000",
        "http://127.0.0.1:3005",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(session.router)
app.include_router(progress.router)

@app.get("/")
def read_root():
    return {"message": "AI Interview Coach API is running", "status": "online"}
