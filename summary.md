# Project Summary (Tabletop + Python GUI)

## Recent Changes (This Session)
- Economy and salaries
  - Treat scientist salaries as credits (K): CSV values like 2/3 are converted to 2000/3000 during recruitment and payroll.
  - Payroll recalculation in cleanup: sums salaries (Doctor/Professor), converts 2/3 → 2K/3K; overload penalty applied as +1K per scientist if team size > 3.
  - Salary status reset: after a successful payroll, all paid scientists are marked `is_paid=True`; on non-payment, only the first occurrence reduces Reputation by 1 and paid scientists become inactive.
- Round activity tracking
  - Added `Player.round_activity_points` and increment on: publish (+3), hire (+2), complete research (+4), found consortium (+5).
- Grants
  - Heuristic requirements check when taking a grant (Reputation threshold, min. scientist types, domain-specific scientist present, min. 2 scientists, scientists from 2 fields, membership/leadership in a consortium).
  - Government Subvention: available if no grants are eligible; target 6 AP in the round, reward 10K paid at end of round.
- Large Projects
  - Auto-completion at end of round if contributed PB/K meet textual thresholds; rewards parsed from director/member reward text and applied; `is_completed=True` set and logged.
  - Manual “Finish Project” button added in consortium contribution UI (enabled only when requirements met).
- Institute bonuses (first pass)
  - MIT/Stanford: +1 hex when placing hexes for Physics research (applied in scientist activation).
  - Max Planck: +1 PB on every completed research (applied on completion).
  - Cambridge: +2K on research completion and +1 PZ to every publication.
  - Harvard: +1 Reputation for publications with IF ≥ 6.
- Publications: added general Reputation gating heuristic (low Rep blocks high-PZ journals), in addition to card-specific requirements.
- CERN partial: refund +1 PA for consortium actions when using FINANSUJ (added at consortium entry point).

Known limitations from this pass
- The main GUI file `principia_card_ui.py` contains encoding-corrupted strings; I avoided mass replacement in this pass. New strings were added in UTF‑8, but some existing labels/conditions remain malformed.
- Stanford 2× Opportunity bonuses are prepared conceptually, but the code block for applying them has not been fully swapped due to string corruption in the target area; safe application pending normalization.
- Scenario/Crises loader still expects old columns; new ASCII CSVs exist (see below), but loader needs updating to parse new headings and the two-phase crisis model.
- Two separate round counters exist (`self.current_round` vs `self.game_data.current_round`); unify in a follow-up.

## Physical Game: Tabletop/Card Overview
- Core resources: Credits (K), Research Points (PB), Prestige Points (PZ), Reputation (0–5), Action Points (PA), and Hex Tokens.
- Components
  - Research Cards (hex map + basic/bonus rewards); Scientists (Doctorant/Doctor/Professor; salary and hex output); Journals (IF, PB cost, PZ, requirements, special bonus);
  - Grants (requirements, goal, one-off K and per-round bonuses); Opportunities & Intrigues; Consortium Cards; Large Projects (global goals with PB/K/Fulfilment requirements and director/member rewards).
  - Institutes: asymmetrical starting resources and special abilities (e.g., MIT/Stanford: +1 hex Physics; Harvard: +1 Rep on IF≥6; Cambridge: +1 PZ publications; CERN: consortium -1 PA; Max Planck: +1 PB per completed research).
- Turn Structure (per round)
  1) Grants Phase: each player may take at most one eligible grant; if none eligible, Government Subvention is available (target 6 AP in that round → reward 10K at end).
  2) Actions Phase: players play action cards (PROWADŹ BADANIA / PUBLIKUJ / FINANSUJ / ZATRUDNIJ / ZARZĄDZAJ) and spend PA on listed actions.
  3) Cleanup Phase: pay salaries; check grant goals; refresh markets; reset action cards; check end conditions.
- Hex Research System: place hexes from the START towards END; bonus hexes grant immediate rewards; when reaching END, collect the card’s rewards and regain all hex tokens.
- Scenarios & Crises: gameplay modifiers and timed global events; in new CSVs (see below), crises have two halves (preview 2 rounds earlier + full effect on crisis round).

## Python GUI Software Overview
- Entry: `principia_card_ui.py` (Tkinter). Game data loader: `GameData` loads CSVs and creates in-memory cards.
- Hex maps: `hex_research_system.py` provides `HexResearchMap` and `HexMapWidget` to parse and render maps and validate placements.
- Networking: `network_game.py` contains scaffolding (server/client/messages), not central to current changes.
- Notable GUI views
  - Action cards panel (play one, then spend PA on listed actions).
  - Market panels (scientists, journals), research panel with collapsible widgets per active research.
  - Consortium management: founding, joining, contributing PB/credits; (now) button to finish projects when requirements are met.
- End-of-round: payroll (with is_paid reset), grant goal checks, auto-complete Large Projects, subvention processing (6 AP → 10K), then round increment.

## Data Files (CSV) Overview
- Core CSVs at repository root: `karty_badan.csv`, `karty_naukowcy.csv`, `karty_czasopisma.csv`, `karty_granty.csv`, `karty_instytuty.csv`, `karty_wielkie_projekty.csv`, `karty_konsorcja.csv` (descriptive).
- New ASCII files added/overwritten for Excel compatibility:
  - `karty_kryzysy_rozszerzone.csv` — 15 crisis cards (two-part: preview+effect) with descriptive text.
  - `karty_scenariusze.csv` — 10 scenarios with: title, long story, starting conditions, crisis schedule, victory, round limit, modifiers, extra rules.
- Loader updates pending to use new column names and two-phase crisis schedule.

## What To Do Next (Recommended Order)
1) Normalize `principia_card_ui.py` strings to proper UTF‑8
   - Replace corrupted UI strings and action-condition text (e.g., menu labels, action parsing, journal/grant labels) with correct Polish text.
   - Keep functional identifiers intact; avoid breaking existing logic.
2) Finish Stanford & CERN features cleanly
   - Stanford: in `apply_opportunity_effect`, multiply all gains by 2 for Stanford (credits/PB/Rep/hex/AP/PZ); ensure PA addition uses `self.remaining_action_points` for current player only.
   - CERN: ensure -1 PA applies consistently for all consortium-related actions taken under FINANSUJ (both contributions and founding); unify detection logic.
3) Unify round counters
   - Use one authoritative round counter (e.g., `self.current_round`) and mirror into `game_data.current_round` if needed for display.
4) Scenario/Crises loader update
   - Adjust to columns in `karty_scenariusze.csv` (ASCII headings: `Tytul`, `Opis_Fabularny`, `Warunki_Poczatkowe`, `Harmonogram_Kryzysow`, `Warunki_Zwyciestwa`, `Limit_Rund`, `Modyfikatory_Rundy`, `Dodatkowe_Zasady`).
   - Add two-phase crisis timeline: reveal preview 2 rounds before, apply full effect on scheduled round; support reading from `karty_kryzysy_rozszerzone.csv` (`Zapowiedz_*`, `Kryzys_*`).
5) UX polish & hardening
   - In Grants Phase, disable “Weź grant” buttons for ineligible grants (beyond the click-time validation already added).
   - Add visible indicators for subvention progress (e.g., current round AP towards 6/6).
   - Expand Large Projects UI: show parsed requirements & a live-ready/blocked indicator; confirm dialog on finishing project.
6) Institute abilities (full set)
   - Validate and implement the full list from `karty_instytuty.csv` (beyond the ones already implemented in this pass), centralizing modifiers so they apply consistently across the app.

If you want, I can start by normalizing the strings and completing Stanford/CERN implementations, then move to the scenario/crisis loader and round counter unification.

