# Gate A Alembic migrations

The local prototype uses SQLite for development and tests. PostgreSQL remains the target
deployment database through the same `DATABASE_URL` setting. Run from `backend` with the
confirmed project Python executable:

```powershell
& $pyExe -m alembic upgrade head
```

The first revision creates the complete Gate A schema from the SQLAlchemy 2 metadata. No
patient records or secrets are stored in the migration files.
