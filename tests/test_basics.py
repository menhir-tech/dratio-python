import unittest


class PackageTest(unittest.TestCase):
    """
    Basic test suite to check if the package can be imported
    """
    def test_import(self):
        """
        Basic test to check if the package can be imported
        """
        from dratio import Client
        self.assertIn("dratio.io", Client.BASE_URL)
        
    def test_version(self):
        """
        Basic test to check __version__ constant
        """
        from dratio import __version__
        self.assertRegex(__version__, r'^\d+\.\d+\.\d+$')
        
if __name__ == "__main__":
     unittest.main()