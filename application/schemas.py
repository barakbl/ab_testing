from typing import List, Union

from pydantic import BaseModel
from datetime import datetime


class View(BaseModel):
    id: int
    variant_id: int
    created_on: datetime


class Experiment(BaseModel):
    id: int = None
    name: str
    is_active: bool = True
