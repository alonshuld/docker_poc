"""
Purpose: Image class that will contain all needed information
Author: Hanich 10
"""

from pydantic import BaseModel, Field
from uuid import UUID, uuid4
import datetime
from dockfile import Dockerfile


class Image(BaseModel):
    """
    Holds all information that image needs
    """

    name: str
    id: UUID = Field(default_factory=uuid4)
    creation_date: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now().replace(microsecond=0))
    dependency_dir: str
    dockerfile: Dockerfile = Field(default_factory=Dockerfile)
