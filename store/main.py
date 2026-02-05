from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from store.core.config import settings
from store.routers import api_router
from store.core.exceptions import NotFoundException, CollisionException
from fastapi.middleware.cors import CORSMiddleware

class App(FastAPI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            **kwargs,
            version="0.0.1",
            title=settings.PROJECT_NAME,
            root_path=settings.ROOT_PATH,
        )

app = App()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message},
    )


@app.exception_handler(CollisionException)
async def collision_exception_handler(request: Request, exc: CollisionException):
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message},
    )

app.include_router(api_router)