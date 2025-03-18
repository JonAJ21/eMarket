from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="Market",
        docs_url="/api/docs",
        description="Market API",
    )
    
    return app