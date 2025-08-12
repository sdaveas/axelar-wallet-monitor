import os
from lcd import lcd_get

AXELAR_LCD = os.getenv("AXELAR_LCD")
FILE_PATH = "data/height.txt"


def update_height(height):
    with open(FILE_PATH, 'w') as file:
        file.write(str(height))


def get_latest_height_from_chain() -> int:
    data = lcd_get("/cosmos/base/tendermint/v1beta1/blocks/latest")
    height = int(data["block"]["header"]["height"])
    return height


def read_height_from_file() -> int:
    if not os.path.exists(FILE_PATH):
        return 0

    with open(FILE_PATH, 'r') as file:
        content = file.read().strip()
        return int(content) if content else 0
