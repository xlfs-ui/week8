# Week4 API Tests Study Notes

## Test Scope

This test set covers all Week4 note and action item HTTP interfaces in `backend/app/routers`.

- Notes APIs:
  - `GET /notes/`
  - `POST /notes/`
  - `GET /notes/search/`
  - `GET /notes/{note_id}`
  - `PUT /notes/{note_id}`
  - `DELETE /notes/{note_id}`
- Action Items APIs:
  - `GET /action-items/` (with and without `completed=true/false`)
  - `POST /action-items/`
  - `PUT /action-items/{item_id}/complete`
  - `PUT /action-items/{item_id}/uncomplete`
  - `DELETE /action-items/{item_id}`

## Coverage Checklist

### Notes

- create and list notes
- update and delete note
- get single note by id
- search by title/content keyword
- not-found behavior for get/update/delete returns `404`

### Action Items

- create -> complete -> uncomplete lifecycle
- list with `completed=true`
- list with `completed=false`
- list without filter returns all records
- delete action item
- not-found behavior for complete/uncomplete/delete returns `404`

## How To Run

From `week4` directory:

```bash
set PYTHONPATH=. && python -m pytest -q backend/tests
```

Or run only API tests:

```bash
set PYTHONPATH=. && python -m pytest -q backend/tests/test_notes.py backend/tests/test_action_items.py
```

## Notes

- Tests use temporary SQLite files via fixture in `backend/tests/conftest.py`.
- Each test case is isolated and uses dependency override for `get_db`.
