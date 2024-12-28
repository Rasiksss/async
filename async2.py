import asyncio
import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from random import randint
import time
app = FastAPI()

@app.get("/numbers")
def number(x: int, y: int):
    try:
        if not(x >=0 and isinstance(x, int) and isinstance(y, int)):
            return  JSONResponse(status_code=422, content={"Error": "Ошибка 422", "ErrorMessage": "Типы данных не являются валидными", "Requestdata":f"x = {x}, y = {y}"})
        result = (x / y) * randint(-10, 10)
    except ZeroDivisionError as e:
        return JSONResponse(status_code=400, content={"Error": "Ошибка 400", "ErrorMessage": "Деление на ноль невозможно", "Requestdata":f"x = {x}, y = {y}"})
    return {"x": x, "y": y, "result": result}

async def fetch(client, x, y):
    start_time = time.time()
    try:
        response = await client.get(f"http://localhost:8000/numbers?x={x}&y={y}")
        response.raise_for_status()
        return (time.time() - start_time, response.json())
    except httpx.HTTPStatusError as e:
        return e.response.json()

async def main():
    async with httpx.AsyncClient() as client:
        tasks = [asyncio.create_task(fetch(client, 10, 2)),
            asyncio.create_task(fetch(client, 20, 0)),  # Ошибка деления на ноль
            asyncio.create_task(fetch(client, -5, 3)),  # Ошибка валидации
            asyncio.create_task(fetch(client, 15, 5)),
            asyncio.create_task(fetch(client, 30, 'abc'))  # Ошибка валидации
                 ]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        results = [task.result() for task in done]
        sorted_done = sorted(results, key=lambda t: t[0] if isinstance(t, tuple) else float('inf'))
        if len(sorted_done) > 1:
            second_result = sorted_done[1]
            print(f"Результат второго по времени выполнения запроса: {second_result}")
        for task in pending:
            task.cancel()
if __name__ == "__main__":
    asyncio.run(main())