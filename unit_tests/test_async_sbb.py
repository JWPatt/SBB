import unittest
import core_func.sbb_api_asyncio
# import json   # uncomment to set the accepted results


class TestSBBModule(unittest.TestCase):
    """Test for the full SBB API querying module"""

    origin_city = 'Davos'
    destinations = {'Landquart'}
    sbb_results = core_func.sbb_api_asyncio_wrapper(origin_city, destinations)

    # Uncomment to set the accepted results
    # save_file = open('sbb_module_accepted_results.json', 'w')
    # json.dump(sbb_results, save_file)
    # save_file.close()

    def test_api_get(self):
        self.assertEqual(True, isinstance(self.sbb_results, dict))


if __name__ == '__main__':
    unittest.main()
