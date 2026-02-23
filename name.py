from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User2(BaseModel):
    name : str
    age : int
    

@app.post("/user2")
def get_name(user:User2):
    return {
        "Messages" : f"Your name '{user.name}' and your age '{user.age}'"
    }
    
