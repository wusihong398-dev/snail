from pydantic import BaseModel



class AIConfigCreate(BaseModel):

    name:str

    display_name:str="蜗牛小精灵"

    provider:str

    api_url:str

    api_key:str

    model:str


    proxy_id:int|None=None


    system_prompt:str=""


    enabled:bool=True

    priority:int=1





class AIConfigResponse(BaseModel):

    id:int

    name:str

    display_name:str|None=None

    provider:str

    model:str

    proxy_id:int|None=None

    enabled:bool

    priority:int


    class Config:

        from_attributes=True
