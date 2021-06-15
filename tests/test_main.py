from super_tiles.main import supertiles
import unittest
import sys

sys.path.append("..")


class test(unittest.TestCase):
    def test_results(self):
        """Test the returned results"""

        for zoom in range(1, 20):
            features = supertiles(
                "https://gist.githubusercontent.com/Rub21/7908291b40d527ca7729c671a9e4ae22/raw/3ab630814f2ff1184179a19eab4f4e85e2f281f5/data.json",
                zoom,
                "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                "tms",
                "data/tiles",
                "data/supertiles",
                "data/supertiles.geojson",
                True,
            )

            tiles_list = features[0]["properties"]["tiles_list"]
            self.assertEqual(len(tiles_list), 4)
