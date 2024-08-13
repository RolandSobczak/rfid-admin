from pydantic import BaseModel


class DeploymentSchema(BaseModel):
    name: str
    ready: bool
