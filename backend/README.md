# BusYatra Backend

## Database Migrations

This backend uses Alembic for schema migrations. FastAPI startup no longer
creates or mutates tables automatically.

From this `backend/` directory:

```powershell
alembic upgrade head
```

To create a new migration after changing SQLAlchemy models:

```powershell
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```
