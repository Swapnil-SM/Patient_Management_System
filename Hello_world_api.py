from fastapi import FastAPI

app = FastAPI() # creating a FastAPI instance(object)

@app.get("/") # creating a route for GET request
def hello():
    return {"message": "Hello, World!"}

@app.get("/about") # creating another route for GET request
def about():
    return {"message": "This is a simple Hello World API using FastAPI."}