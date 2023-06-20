from typing import Union
from typing_extensions import Annotated
import uvicorn
from fastapi.responses import HTMLResponse
from fastapi import Depends
from sqlalchemy.orm import Session
import os
from fastapi import FastAPI, Header
from application.experiment import get_experiment

from application import models
from application.database import engine, get_db

import logging
import sys

stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [stdout_handler]

logging.basicConfig(
    level=os.environ.get("LOG)LEVEL", logging.DEBUG),
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
    handlers=handlers,
)


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def homepage_ctrl():
    return """
    
     <a href="http://localhost:8888/docs">API (Swagger)</a> <br>"
    """


@app.get("/experiment/{name}")
def experiment_endpoint(
    name: str,
    deviceID: Annotated[Union[str, None], Header()],
    db: Session = Depends(get_db),
):
    experiment = get_experiment(db, name, deviceID)
    return experiment


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.environ.get("IP", "0.0.0.0"),
        port=os.environ.get("PORT", 8888),
        reload=True,
    )
