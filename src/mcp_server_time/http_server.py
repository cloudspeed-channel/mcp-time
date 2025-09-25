from fastapi import FastAPI
from datetime import datetime
import os
import pytz

from .server import TimeServer, get_local_tz

app = FastAPI(title="MCP Time Server HTTP API")

time_server = TimeServer()

@app.get("/time/current")
def get_current_time(timezone: str | None = None):
    """Return the current time in a given timezone (default: LOCAL_TIMEZONE)"""
    if not timezone:
        timezone = str(get_local_tz())
    result = time_server.get_current_time(timezone)
    return result.model_dump()

@app.get("/time/convert")
def convert_time(source_timezone: str, time: str, target_timezone: str):
    """Convert time from one timezone to another"""
    result = time_server.convert_time(source_timezone, time, target_timezone)
    return result.model_dump()
