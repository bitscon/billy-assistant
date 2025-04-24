import os

PROFILE_PATH = os.getenv('PROFILE_PATH', 'data/user_profile.json')
OLLAMA_URL = os.getenv('OLLAMA_URL',  'http://ollama:11434/api/generate')
DEFAULT_SEARCH_PROVIDER = 'duckduckgo'
