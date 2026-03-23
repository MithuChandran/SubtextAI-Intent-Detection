import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router as api_router
from src.model.interface import DissonanceClassifier

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model once at startup
    model_path = os.environ.get("MODEL_PATH", "models/intent30_text_emoji_baseline")
    classifier = DissonanceClassifier(model_path)
    classifier.load()
    app.state.classifier = classifier
    yield
    # Clean up if needed
    del app.state.classifier

app = FastAPI(
    title="Subtext AI: Dissonance Analyzer", 
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Subtext AI API is running. Use /docs for documentation."}

