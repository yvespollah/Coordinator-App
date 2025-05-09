"""
Configuration Redis pour le projet.
"""

# Configuration Redis
REDIS_HOST = 'localhost'  # Hôte Redis
REDIS_PORT = 6379         # Port Redis standard
REDIS_DB = 0              # Base de données Redis

# Configuration du proxy Redis
REDIS_PROXY_HOST = 'localhost'  # Hôte du proxy Redis
REDIS_PROXY_PORT = 6380         # Port du proxy Redis
REDIS_PROXY_DB = 0              # Base de données du proxy Redis

# Configuration pour les services qui doivent utiliser le proxy
USE_REDIS_PROXY = True     # Utiliser le proxy Redis au lieu de Redis directement
