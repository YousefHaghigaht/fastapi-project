from fastapi import FastAPI
from routers import (
    user_routers,
    book_routers
)


app = FastAPI(
    title='This FastAPI test project',
    swagger_ui_parameters={
        "persistAuthorization": True
    })


app.include_router(user_routers.router)
app.include_router(book_routers.router)
