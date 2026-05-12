from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.graphql.schema import get_graphql_router
from app.graphql.context import get_graphql_context

from app.db.database import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Dispose the engine on shutdown
    await engine.dispose()

app = FastAPI(title="BusYatra API", version="0.1.0", lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── GraphQL ──────────────────────────────────────────────────────────────────
# Mounts the full GraphQL API at /graphql
# - GraphiQL playground: http://localhost:8000/graphql  (browser)
# - API endpoint:        POST http://localhost:8000/graphql  (clients)
graphql_router = get_graphql_router(context_getter=get_graphql_context)
app.include_router(graphql_router, prefix="/graphql")

@app.get("/")
def home():
    return {"message": "BusYatra API - visit /graphql for the GraphQL playground"}
