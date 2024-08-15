from typing import List
from pydantic import BaseModel


class ContainerSchema(BaseModel):
    name: str
    image: str


class DeploymentSchema(BaseModel):
    name: str
    ready: bool
    containers: List[ContainerSchema]
