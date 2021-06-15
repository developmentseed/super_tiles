from super_tiles.main import main
import unittest
import sys

sys.path.append("..")


class TestSortRows(unittest.TestCase):
    def test_results(self):
        """Test the returned results"""
        for zoom in range(1, 20):
            features = main(
                geojson_file="https://gist.githubusercontent.com/Rub21/7908291b40d527ca7729c671a9e4ae22/raw/3ab630814f2ff1184179a19eab4f4e85e2f281f5/data.json",
                zoom=zoom,
                url_map_service="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                url_map_service_type="tms",
                tiles_folder="data/tiles",
                st_tiles_folder="data/supertiles",
                geojson_output="data/supertiles.geojson",
            )

        tiles_list = features[0]["properties"]["tiles_list"]
        self.assertEqual(len(tiles_list), 4)
