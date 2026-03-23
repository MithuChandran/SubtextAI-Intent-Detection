import shutil
import os
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter()

class AnalysisResponse(BaseModel):
    filename: str
    status: str
    message: str
    results: list = Field(default_factory=list)

@router.get("/info")
async def get_info(request: Request):
    """Return information about the currently loaded model"""
    classifier = getattr(request.app.state, "classifier", None)
    return {
        "status": "online" if classifier else "model_not_loaded",
        "model_path": classifier.model_path if classifier else None,
        "device": str(classifier.device) if classifier else None,
        "features": ["emoji_support", "batch_inference", "lifespan_caching"]
    }

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_chat_log(request: Request, file: UploadFile = File(...)):
    # Validate file type
    if not file.filename or not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    # Get cached classifier from app state
    classifier = getattr(request.app.state, "classifier", None)
    if not classifier:
        raise HTTPException(status_code=503, detail="Model is still loading or not initialized")

    # Save temp file
    temp_dir = "data/uploads"
    os.makedirs(temp_dir, exist_ok=True)
    safe_name = Path(file.filename).name
    file_location = os.path.join(temp_dir, f"{uuid4().hex}_{safe_name}")
    
    try:
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        # Process File
        from src.parser.whatsapp_parser import WhatsAppParser
        parser = WhatsAppParser()
        df = parser.parse_file(file_location)
        
        if df.empty:
            return {
                "filename": safe_name,
                "status": "processed",
                "message": "No valid messages found in file.",
                "results": []
            }

        # Batch Inference for significant speedup
        messages = df['message'].tolist()
        emojis = df['emoji'].tolist()
        
        # Perform batch prediction
        predictions = classifier.predict_batch(messages, emojis)
        
        results = []
        for i, row in df.iterrows():
            pred = predictions[i]
            results.append({
                "timestamp": row['timestamp'],
                "sender": row['sender'],
                "message": row['message'],
                "emoji": row['emoji'],
                "dissonance_score": pred['dissonance_score'],
                "label": pred['label'],
                "dissonance_level": pred.get('dissonance_level', pred['label']),
                "dialogue_act": pred.get('dialogue_act', "Neutral"),
                "dialogue_act_confidence": pred.get('dialogue_act_confidence', 1.0),
            })
            
        message = f"Successfully analyzed {len(df)} messages using batch inference."
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        # Cleanup temp file
        if os.path.exists(file_location):
            os.remove(file_location)

    return {
        "filename": safe_name,
        "status": "processed",
        "message": message,
        "results": results
    }
