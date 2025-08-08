import os
from lcd import lcd_get

AXELAR_LCD = os.getenv("AXELAR_LCD")
FILE_PATH = "data/height.txt"


def update_height() -> int:
    height = _get_latest_height_from_chain()
    with open(FILE_PATH, 'w') as file:
        file.write(str(height))
    
    return height


def get_height() -> int:
    height = _read_height_from_file(FILE_PATH)
    if height == 0:
       height = update_height()
        
    return height


def _get_latest_height_from_chain() -> int:
    data = lcd_get("/cosmos/base/tendermint/v1beta1/blocks/latest")
    height = int(data["block"]["header"]["height"])
    return height


def _read_height_from_file(file_path:str) -> int:
    if not os.path.exists(file_path):
        return 0

    with open(file_path, 'r') as file:
        content = file.read().strip()
        return int(content) if content else 0
