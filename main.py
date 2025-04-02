#!/usr/bin/env python3

from fastapi import FastAPI

app = FastAPI()
app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
  
