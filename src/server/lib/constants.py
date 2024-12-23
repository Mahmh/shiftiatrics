from dotenv import load_dotenv; load_dotenv()
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # path with respect to this file

ENABLE_LOGGING = (os.getenv('ENABLE_LOGGING', 'true').lower() == 'true')