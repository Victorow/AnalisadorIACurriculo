from pydantic import BaseModel

class job(BaseModel):
    id: str
    name: str
    main_activities: str
    prerequisites: str
    differentials: str