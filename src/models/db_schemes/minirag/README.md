## Run Alembic Migrations

## Configuration

```bash
cp alembic.ini.example alembic.ini
```

* Update the `alembic.ini` with your database credentials

---

## (Optional) Create a new migration

```bash
alembic revision --autogenerate -m "Add .."
```

---

## Upgrade the database

```bash
alembic upgrade head
```

---

## Rollback the last migration

```bash
alembic downgrade -1
```

---

## Rollback to specific revision

```bash
alembic downgrade <revision_id>
```

---

## Show migration history

```bash
alembic history
```

---

## Show current database version

```bash
alembic current
```

---

## Upgrade step by step

```bash
alembic upgrade +1
```

---

## Reset database (⚠️ destructive)

```bash
docker compose down -v
docker compose up -d
alembic upgrade head
```

---

## Notes

* Do not commit sensitive data (e.g., database credentials)
* Do not modify the database manually (e.g., DBeaver)
* Always use Alembic for schema changes
* Use clear migration names (e.g., "add_users_table", "remove_column")
