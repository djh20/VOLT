from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from volt.db import db

app = FastAPI()

@app.get("/api/measurements")
async def get_measurements():
    return db.xrevrange("measurements", count=5)

# Serve frontend
app.mount(
    "/", 
    StaticFiles(directory="frontend-dist", check_dir=False, html=True),
    name="frontend"
)