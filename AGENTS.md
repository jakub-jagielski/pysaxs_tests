# Repository Guidelines

## Project Structure & Modules
- `principia_card_ui.py` — Tkinter GUI and core gameplay loop.
- `hex_research_system.py` — hex map parsing, rules, and `HexMapWidget` rendering.
- `network_game.py` — local sockets for multiplayer (server/client, messages).
- `generate_cards.py` — PNG card generator from CSVs in repo root (`karty_*.csv`).
- Assets: `graphics/` prompts and references; outputs in `cards/`.
- Docs: `instrukcja.md`, `README_GRA.md`, `GRA_SIECIOWA_INSTRUKCJA.md`, `testing.md`.

## Build, Run, Test
- Setup: `python -m venv .venv` → activate → `pip install pillow pandas`.
- Run GUI: `python principia_card_ui.py`.
- Generate cards: `python generate_cards.py` → images in `cards/`.
- Visual checks: `python test_hexagon.py`; parser checks: `python test_new_format.py`.
- Optional lint/format: `pip install black ruff && black . && ruff .`.

## Game Mechanics & Data
- Mechanics: action cards (Research/Hire/Publish/Finance/Manage), grants, journals, hex‑based research, reputation, prestige (PZ), research points (RP), and credits (K). Keep changes aligned with `instrukcja.md`.
- Data source: CSVs `karty_*.csv` (badania, naukowcy, granty, itd.). Keep headers stable and Polish copy consistent; update loaders if schemas change.
- Hex map strings: one START, a single main path to END, optional dead‑end branches with BONUS.
  Example: `START(0,0)->[(1,0)->(2,0)END | (0,1)->BONUS(+1PZ)]`.

## Testing & Verification
- Follow `testing.md` scenarios: round flow, action points, hex placement, grants, publications, scientists.
- Economy checks: salaries in cleanup; government subsidy (target 6 AP, +10K) works; reputation gates for high‑impact journals; overload penalties; RP/K/PZ rewards match card text.
- Determinism: seed RNG in new tests for reproducibility (`random.seed(42)`).
- Cards: verify text wrapping and clipping in generated PNGs; do not commit `cards/` outputs.

## Style & Naming
- Python 3.9+, PEP 8, 4 spaces. snake_case for functions/vars, PascalCase for classes.
- Filenames: `principia_*.py`, helpers `*_system.py`, data `karty_*.csv`.
- Keep UI/data strings in Polish with UTF‑8 diacritics.

## Commits & PRs
- Conventional Commits (`feat(ui): …`, `fix(hex): …`, `docs: …`).
- PRs: description, linked issues, screenshots/GIFs for UI, CSV diffs, and run steps. Update docs and `testing.md` when mechanics/economy change.

## Security & Config
- Networking on `localhost:8888`; avoid public exposure. If enabling remote play, document ports and risks in `GRA_SIECIOWA_INSTRUKCJA.md`.
- When CSV schemas change, migrate generators and UI together so rules, economy, and cards stay in sync.
