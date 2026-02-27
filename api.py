import json
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import run_full_scan
from backend.pipeline import run_pipeline
from reports.report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="Strider PII API")

class ScanRequest(BaseModel):
    target: str = ""

@app.post("/api/scan")
def api_scan(req: ScanRequest):
    logger.info(f"Received scan request for target: {req.target}")
    
    # 1. Run Core Scrapers
    docs = run_full_scan(req.target if req.target else None)
    
    # 2. Run NLP/Regex Pipeline
    incidents = run_pipeline(docs)
    
    # 3. Generate structured JSON report
    generator = ReportGenerator()
    report = generator.generate(incidents)
    
    # 4. Save report so dashboard.html fetches it reliably
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / "scan_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    return JSONResponse(content={"status": "success", "message": "Scan complete", "report": report})

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    dashboard_path = Path("reports") / "dashboard.html"
    if not dashboard_path.exists():
        return "<h1>Dashboard generated file not found. Run python generate_dashboard.py first.</h1>"
    return dashboard_path.read_text(encoding="utf-8")

# Mount the reports directory so scan_report.json and other files can be fetched
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

if __name__ == "__main__":
    import uvicorn
    # Run on 8080 to avoid conflicts if the user is keeping 8000 alive
    uvicorn.run(app, host="0.0.0.0", port=8080)
