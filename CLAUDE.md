# Compost Tracker

Django app for tracking horse manure compost piles through their stages.
Run things with `uv run` (e.g. `uv run pytest`, `uv run python manage.py runserver`).

## Requirements (jamb)

Requirements live in `reqs/` as YAML and are managed with `uv run jamb`.

- `PRJ` (`reqs/prj`): the project itself, one item.
- `UN` (`reqs/un`): user needs, written in Bernie's voice, saying *why*.
  No implementation detail.
- SRS documents, one per area of the app as the user sees it, all under `reqs/srs/`:
  `HOME` (home page), `PILE` (Add Pile, pile list, pile page), `LOG` (Add Log),
  `STAGE` (Locations page, stage durations). Listed in `test_documents` in
  `pyproject.toml`; tests link to these, never to UN.

Rules:

- Only Bernie approves requirements. Never run `jamb review` (`mark`, `clear` or
  `reset`), and never write `reviewed:` values or link hashes by hand.
  `.claude/settings.json` denies these commands.
- Never use `--before`/`--after` or `jamb reorder`; UIDs are permanent names.
- Behavior changes go through `/req-feature`: requirement first, then a failing
  test marked `@pytest.mark.requirement("<SRS UID>")`, then the code.

## Code style

- One import per line, sorted.
- Tests in `pile_tracker/tests.py`, using pytest-django fixtures (`client`, `db`).
