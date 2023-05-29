from typing import Annotated

from fastapi import FastAPI, Query, Path, Body
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"}
]


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, description='The description of the item.', max_length=20
    )
    price: float = Field(
        gt=0, description="The price must be greater than zero")
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


class User(BaseModel):
    username: str
    full_name: str | None = None


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app: FastAPI = FastAPI()


@app.get('/')
async def root():
    return {"message": "Hello World!"}


@app.get('/items')
async def get_items_data(skip: int = 0, limit: int = 10, hidden_query: bool | None = Query(default=None, include_in_schema=False)):
    return fake_items_db[skip: skip + limit] if not hidden_query else {'secret code': '007'}


@app.get('/items/{item_id}')
async def get_specific_item_data(needy: str, item_id: int = Path(title='ID deel producto a buscar', ge=1), q: str | None = Query(default=None, max_length=5, regex='^[abc]\w+q$'), short: bool = False):
    item = {"item_id": item_id, 'needy': needy}
    if q:
        item.update({'q': q})
    if not short:
        item.update({"description": "Item description here."})
    return item


@app.post('/items')
async def create_item(item: Item):
    return item


@app.get("/users/{user_id}/items/{item_id}")
async def get_user_item(user_id: int = Path(le=3), item_id: int = Path(gt=0, le=5), q: str | None = Query(default=...), short: bool = False):
    item = {"user_id": user_id, "item_id": item_id}
    if q:
        item.update({'q': q})
    if not short:
        item.update({'description': 'item description hereeee.'})
    return item


@app.get('/users/me')
async def get_own_user_data():
    return {"user_id": 'own user'}


@app.get('/users/{user_id}')
async def get_user_data(user_id: str, q: list[str] | None = Query(default=["foo", "bar", "zoo"], title='Query String', description='Testing queries', alias='item-query', deprecated=True)):
    res = {"user_id": user_id, 'q': q}
    return res


@app.get('/models/{model_name}')
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# Asi este no se ejecuta porque el read_file agarra todas las entradas
@app.get("/files/{file_path}")
async def read_file_2(file_path: str):
    return {"file_path_2": file_path}


@app.put("/items/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    item: Annotated[Item, Body(embed=True)],
    q: str | None = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results


@app.put("/itemz/{item_id}")
async def update_item_2(
    item_id: int, item: Item, user: User, importance: Annotated[int, Body(gt=0)]
):
    results = {"item_id": item_id, "item": item,
               "user": user, "importance": importance}
    return results


@app.post("/offers")
async def create_offer(offer: Offer):
    return offer

@app.post("/images/multiple")
async def create_multiple_image(images: list[Image]):
    return images

@app.post("/index-weights")
async def create_index_weights(weights: dict[int, float]):
    return weights


# uvicorn.exe main:app --reload
