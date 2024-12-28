from fastapi import FastAPI
import httpx
import asyncio
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
                 asyncio.create_task(fetch(client, 20, 1)),
                 asyncio.create_task(fetch(client, 5, 3)),
                 asyncio.create_task(fetch(client, 15, 5)),
                 asyncio.create_task(fetch(client, 30, 4))
                 ]

        done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        result = [task.result() for task in done]
        sorted_done = sorted(result, key=lambda t: t[0] if isinstance(t, tuple) else float('inf'))
        if sorted_done[2][1]["result"] < 0:
            for task in pending:
                task.cancel()
            print( {
                "first_time": sorted_done[0][1]["result"],
                "second_time": sorted_done[1][1]["result"]
            })
        else:
            print({
                "fouth_time": sorted_done[3][1]["result"],
                "fifth_time": sorted_done[4][1]["result"]
            })

if __name__ == "__main__":
    asyncio.run(main())