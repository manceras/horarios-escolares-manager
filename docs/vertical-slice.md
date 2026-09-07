# Adding a feature end to end

Follow this recipe literally. `Teacher` is the reference implementation: every
file listed below already exists for it, so copy it and adapt.

Example task: expose `Room`.

## 1. Model — `backend/app/models/room.py`

```python
class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
```

Import it in `app/models/__init__.py` so Alembic sees it.

## 2. Migration

```sh
make migration name=add_rooms
```

Read the generated file before committing it; autogenerate is a draft.

## 3. Schemas — `backend/app/schemas/room.py`

`RoomCreate`, `RoomUpdate` (all fields optional) and `RoomRead`
(`model_config = ConfigDict(from_attributes=True)`).

## 4. Repository — `backend/app/repositories/room_repository.py`

Queries only. Extend `BaseRepository[Room]` and add the specific lookups the
service needs (`get_by_name`, ...). No validation, no rules.

## 5. Service — `backend/app/services/room_service.py`

Business rules and invariants. Raises `NotFoundError` / `ConflictError` from
`app/core/errors.py`, never `HTTPException`. Owns the transaction boundary
(`session.commit()`).

## 6. Router — `backend/app/api/v1/rooms.py`

Thin. Declares the path and the response model, then calls the service. Register it in `app/api/v1/router.py`.

```python
@router.get("", response_model=list[RoomRead])
def list_rooms(service: RoomServiceDep) -> Sequence[Room]:
    return service.list_all()
```

## 7. Test — `backend/tests/test_rooms.py`

At least: happy path, the rule that makes this entity special, and one failure
case (404 or 409).

## 8. Regenerate the client

```sh
make gen-api
```

## 9. Frontend feature — `frontend/src/features/rooms/`

```
api.ts        TanStack Query hooks built on the generated client
RoomTable.tsx presentation
RoomForm.tsx  create / edit form
```

Query keys go in `src/lib/api/query-keys.ts`.

## 10. Route — `frontend/src/routes/RoomsPage.tsx`

Composition only: title, the feature components, loading and error states.
Register it in `src/app/router.tsx` and add its nav entry.

## 11. Translations — `frontend/src/locales/es.json`

Every visible string, under a `rooms.*` namespace.

## 12. Gate

```sh
make check
```

## Checklist before reporting done

- [ ] `make check` passes
- [ ] migration created and reviewed
- [ ] tests for the new rule
- [ ] `make gen-api` run and the UI compiles against the new types
- [ ] no Spanish outside `es.json`
- [ ] no layer skipped
