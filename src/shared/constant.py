from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

URL = "https://stopots.com/pt"
NICKNAME = "Luis"

STATE_PATH = BASE_DIR / "state.json"
CSV_PATH = BASE_DIR / "palavras_stop.csv"

ASSETS_DIR = BASE_DIR / "assets"

IMAGEM_AGUARDANDO = ASSETS_DIR / "aguardando.png"
IMAGEM_AVALIAR = ASSETS_DIR / "avaliar.png"
IMAGEM_AVALIAR_OFF = ASSETS_DIR / "avaliar_off.png"
IMAGEM_FILL = ASSETS_DIR / "fill.png"
IMAGEM_READY = ASSETS_DIR / "ready.png"