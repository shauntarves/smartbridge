import unittest
from .wyze_provider_tests import *
from os.path import join, dirname
from dotenv import load_dotenv

# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')

# Load file from the path.
load_dotenv(dotenv_path)

if __name__ == '__main__':
    unittest.main()
