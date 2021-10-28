import os
from PIL import Image
import logging
from smart_open import open

logger = logging.getLogger(__name__)


def stitcher_tiles(tiles_list_paths, stile_file_name):
    """Merge tiles in one supertile

    Args:
        tiles_list_paths (list): list of tiles path
        stile_file_name (str): supertile path

    """
    try:
        filepaths = [filep for filep in tiles_list_paths if filep != "_"]

        def xy(filepath):
            base = os.path.basename(filepath)
            x, y, z = base.split("-")
            y = os.path.splitext(y)[0]
            return int(x), int(y)

        # def yx(filepath):
        #     return xy(filepath)[::-1]

        filepaths = sorted(filepaths, key=xy)

        if len(filepaths) == 0:
            logger.info("No files found")
            raise SystemExit

        with open(filepaths[0], "rb") as image_tile:
            tile_w, tile_h = Image.open(image_tile).size

        xys = list(map(xy, filepaths))

        x_0, y_0 = min(map(lambda x_y: x_y[0], xys)), min(map(lambda x_y: x_y[1], xys))
        x_1, y_1 = max(map(lambda x_y: x_y[0], xys)), max(map(lambda x_y: x_y[1], xys))

        n_x, n_y = (x_1 - x_0 + 1), (y_1 - y_0 + 1)
        out_w, out_h = n_x * tile_w, n_y * tile_h

        out_img = Image.new("RGBA", (out_w, out_h), (0, 0, 255, 0))
        for filepath in filepaths:
            x, y = xy(filepath)
            x, y = x - x_0, y - y_0
            with open(filepath, "rb") as ftile:
                tile = Image.open(ftile)
                out_img.paste(
                    tile,
                    box=(x * tile_w, y * tile_h, (x + 1) * tile_w, (y + 1) * tile_h),
                )

        with open(stile_file_name, "wb") as sfile:
            out_img.save(sfile)

        return stile_file_name
    except Exception as ex:
        logger.error(ex.__str__())
        pass
