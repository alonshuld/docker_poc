"""
Purpose: Image class that will contain all needed information
Author: Hanich 10
"""


from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from dockfile import Dockerfile


class Image(BaseModel):
    """
    Holds all information that image needs
    """
    name: str
    id: UUID = Field(default_factory=uuid4())
    creation_date: datetime = Field(default_factory=datetime.today())
    dependency_dir: str
    dockerfile: Dockerfile = Dockerfile()
