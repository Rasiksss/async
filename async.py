from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import date, timedelta
from pydantic import BaseModel, conint
from random import randint
import asyncio
import httpx

app = FastAPI()

@app.get("/sum")
def read_root(a: int, b: int) -> JSONResponse:
    result = a + b
    return JSONResponse(content={'result': result})

@app.get("/sum_date")
def sum_date(current_date: date, offset: int) -> JSONResponse:
    result = current_date + timedelta(days=offset)
    return JSONResponse(content={'result': result.isoformat()})

@app.post("/user")
def print(name: str):
    return {"message": f"Hello, {name}"}


class User(BaseModel):
    name: str
    surname: str
    age: int
    registration_date: date


@app.post("/user/validate")
def user_validate(user: User):
    return {"message": f"Wild add user: {user.name} {user.surname} with age {user.age}"}


class Number(BaseModel):
    x: conint(gt=0)
    y: int


@app.get("/numbers")
def div(x: int, y: int):
    try:
        if not (x >= 0 and isinstance(y, int) and isinstance(x, int)):
            return JSONResponse(
                status_code=422,
                content={"Error": "422 Unprocessable Entity", "ErrorMessage":
                "Тип данных не является валидным", "RequestData": f"x = {x}; y = {y}"})
        result = (x / y) * randint(-10, 10)
    except ZeroDivisionError as z:
        return JSONResponse(status_code=400, content={"Error": "400", "ErrorMessage": "Ошибка деления на ноль", "RequestData": f"x = {x}; y = {y}"})
    return {"x": x, "y": y, "result": result}

async def fetch(client, x, y):
    try:
        response = await client.get(f"http://localhost:8000/numbers?x={x}&y={y}")
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        return e.response.json()

async def main():
    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, 10, 2),
            fetch(client, 20, 0),  # Ошибка деления на ноль
            fetch(client, -5, 3),   # Ошибка валидации
            fetch(client, 15, 5),
            fetch(client, 30, 'abc') # Ошибка валидации
        ]

        result = await asyncio.gather(*tasks)
        for result in result:
            print(result)

if __name__ == "__main__":
    asyncio.run(main())

