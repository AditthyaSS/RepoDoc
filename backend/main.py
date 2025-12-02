from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from modules.repo_fetcher import RepoFetcher
from modules.dependency_analyzer import DependencyAnalyzer

app = FastAPI(title="DeadRepo Doctor API")

# CORS MUST be above everything else
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------
# Request Models
# ---------------------------
class FetchRequest(BaseModel):
    repo_url: str


class AnalyzeRequest(BaseModel):
    local_path: str


# ---------------------------
# Routes
# ---------------------------
@app.get("/")
def root():
    return {"status": "backend alive"}


@app.post("/api/fetch")
def fetch_repo(request: FetchRequest):
    try:
        fetcher = RepoFetcher()
        path = fetcher.fetch(request.repo_url)
        return {"local_path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
def analyze_repo(request: AnalyzeRequest):
    try:
        analyzer = DependencyAnalyzer()
        report = analyzer.analyze(request.local_path)
        return {"analysis_report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
