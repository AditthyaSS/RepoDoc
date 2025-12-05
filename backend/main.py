from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from modules.repo_fetcher import RepoFetcher
from modules.dependency_analyzer import DependencyAnalyzer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DeadRepo Doctor API")

# ✅ FIXED CORS (ALLOWS ALL ORIGINS — NO MORE FAILED TO FETCH)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow requests from ANY frontend
    allow_credentials=True,
    allow_methods=["*"],          # Allow all HTTP methods
    allow_headers=["*"],          # Allow all headers
)

# ------------------------------
# Request Models
# ------------------------------

class FetchRequest(BaseModel):
    repo_url: str

class AnalyzeRequest(BaseModel):
    local_path: str


# ------------------------------
# API ROUTES
# ------------------------------

# ✅ Fetch / Clone Repo Endpoint
@app.post("/api/fetch")
def fetch_repo(request: FetchRequest):
    try:
        fetcher = RepoFetcher()
        local_path = fetcher.fetch_repo(request.repo_url)

        return {"local_path": local_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Analyze Repo Endpoint
@app.post("/api/analyze")
def analyze_repo(request: AnalyzeRequest):
    try:
        analyzer = DependencyAnalyzer()
        report = analyzer.analyze(request.local_path)

        flat = {
            "total_packages": report["summary"]["total_packages"],
            "outdated_count": report["summary"]["outdated_count"],
            "health_score": report["health_score"],
            "outdated_packages": report["outdated_packages"],
            "partial_analysis": report["partial"]
        }

        return {"analysis_report": flat}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------
# Root Endpoint (Optional)
# ------------------------------
@app.get("/")
def root():
    return {"message": "DeadRepo Doctor API is running!"}
