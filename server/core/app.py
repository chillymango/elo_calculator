from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    from server.routers import (
        auth,
        match,
        player,
        summary,
    )
    app = FastAPI()
    app.include_router(auth.router, prefix="/api")
    app.include_router(match.router, prefix="/api")
    app.include_router(player.router, prefix="/api")
    app.include_router(summary.router, prefix="/api")

    # TODO: fix
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    return app
