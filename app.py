import sys
import os
import certifi
import pandas as pd
from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from uvicorn import run as app_run

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

# ==========================
# ENV & DATABASE SETUP
# ==========================
load_dotenv()
ca = certifi.where()

MONGODB_URL = os.getenv("MONGODB_URL_KEY")

# ==========================
# FASTAPI APP SETUP
# ==========================
app = FastAPI(title="CyberShield - Network Security")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# ==========================
# HOME PAGE (UI)
# ==========================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# ==========================
# PREDICTION ENDPOINT
# ==========================
@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)

        preprocessor = load_object("final_model/preprocessor.pkl")
        model = load_object("final_model/model.pkl")

        network_model = NetworkModel(preprocessor=preprocessor, model=model)
        preds = network_model.predict(df)

        # Example logic
        malicious_count = (preds == 1).sum()
        confidence = int((malicious_count / len(preds)) * 100)

        prediction = "Malicious Traffic" if malicious_count > 0 else "Safe Traffic"

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "prediction": prediction,
                "confidence": confidence
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": str(e)
            }
        )


# ==========================
# MAIN ENTRY POINT
# ==========================
if __name__ == "__main__":
    app_run(
        app,
        host="0.0.0.0",
        port=8080
    )
