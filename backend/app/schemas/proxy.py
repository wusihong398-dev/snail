from pydantic import BaseModel



class ProxyCreate(BaseModel):

    name: str = "代理节点"

    url: str




class ProxyResponse(BaseModel):

    id: int

    name: str

    protocol: str | None = None

    server: str | None = None

    port: int | None = None

    enabled: bool

    status: str



    class Config:

        from_attributes = True
