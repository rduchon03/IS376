from fastapi import FastAPI

app = FastAPI()

restaurant_list = []

@app.get("/restaurants")
async def get_restaurants():
    return {"restaurants": restaurant_list}

@app.post("/restaurants")
async def add_restaurant(name: str):
    restaurant_list.append(name)
    return {"message": f"{name} added."}

@app.delete("/restaurants")
async def clear_restaurants():
    restaurant_list.clear()
    return {"message": "Restaurant list cleared."}
