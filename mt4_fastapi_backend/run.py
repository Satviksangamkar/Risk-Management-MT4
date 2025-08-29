#!/usr/bin/env python3
"""
FastAPI Application Runner
Simple script to run the MT4 FastAPI backend
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print("Starting MT4 FastAPI Backend...")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"API docs: http://localhost:8000/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )
