from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.models.user import User
from app.modules.users.router import router as users_router
from app.models.study_session import StudySession
from app.modules.study.router import router as study_router
from app.models.todo import Todo
from app.modules.todo.router import router as todo_router
from app.modules.ai.router import router as ai_router
from app.models.question import Question
from app.modules.practice.router import router as practice_router
from app.modules.analytics.router import router as analytics_router
from app.modules.dashboard.router import router as dashboard_router

app = FastAPI()

#CORS (Cross-Origin Resource Sharing) FIX 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #for devlopment, in production specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(study_router)
app.include_router(todo_router)
app.include_router(ai_router)
app.include_router(practice_router)
app.include_router(analytics_router)
app.include_router(dashboard_router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Backend is running"}
