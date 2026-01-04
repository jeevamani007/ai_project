from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
from io import BytesIO
from analyzer import analyze_data
import os

app = FastAPI(title="Business Rules Analyst AI")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for frontend assets
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    """Serve the main frontend HTML file"""
    frontend_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "Frontend not found. Please ensure frontend/index.html exists."}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        # Read file content
        contents = await file.read()
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        # Load dataframe based on file type
        df = None
        if file_extension == 'csv':
            df = pd.read_csv(BytesIO(contents))
        elif file_extension in ['xls', 'xlsx']:
            df = pd.read_excel(BytesIO(contents))
        elif file_extension == 'sql':
            # For SQL files, we'll try to execute them (assuming SQLite for simplicity)
            # In production, you might want to support connection strings
            raise HTTPException(status_code=400, detail="SQL file execution requires database connection. Please export to CSV/XLSX first.")
        else:
            # Try CSV as default
            try:
                df = pd.read_csv(BytesIO(contents))
            except:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}. Supported formats: CSV, XLS, XLSX")
        
        # Validate that dataframe is not empty
        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        result = analyze_data(df)
        return result
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Uploaded file is empty or invalid")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")