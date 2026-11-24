# Hardware CAD

Parametric `build123d` models, vendor CAD assets, exports, and renders for the ODrive BotWheel Explorer.

## Onshape API Setup

To fetch vendor assemblies (such as the [ODrive BotWheel Explorer Onshape publication](https://cad.onshape.com/publications/2921014fe168921e9598967c/w/2fb0d2823425b7bd58ea4a32/e/99fdf1e921bf2247872c36a9)) programmatically via the Onshape REST API:

1. Log in to [cad.onshape.com](https://cad.onshape.com) -> **User Icon** -> **My Account** -> **Developer** -> **API keys** -> **Create new API key** (Read scope is sufficient).
2. Copy `.env.template` in the repository root to `.env` (gitignored):
   ```bash
   cp .env.template .env
   ```
3. Fill in `ONSHAPE_ACCESS_KEY` and `ONSHAPE_SECRET_KEY` in `.env`.
4. Fetch the latest STEP and convert to `.xbf`:
   ```bash
   python3 hardware/fetch_onshape.py
   cad step export hardware/vendor/botwheel_explorer.step hardware/vendor/botwheel_explorer.xbf
   ```
