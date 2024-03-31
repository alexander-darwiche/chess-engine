from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials= True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

# Post Movies (create new)
@app.post("/movies/")
async def add_movie():
    test = {'hi':'hi'}
    return test


# Get All Movies (select)
@app.get("/movies/")
async def get_movies():
    test = {'hi':'hi'}
    return test