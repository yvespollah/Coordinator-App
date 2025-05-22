"""
Exemple d'utilisation des fonctions d'authentification pour les managers.
"""

import logging
import sys
import os
import time

# Ajouter le répertoire parent au chemin de recherche pour pouvoir importer redis_communication
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from redis_communication.auth_client import register_manager, login_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def register_callback(response):
    """
    Fonction de rappel pour l'enregistrement.
    
    Args:
        response: Réponse du serveur
    """
    if response.get('status') == 'success':
        logger.info(f"Enregistrement réussi! Manager ID: {response.get('manager_id')}")
        logger.info(f"Username: {response.get('username')}")
        logger.info(f"Email: {response.get('email')}")
    else:
        logger.error(f"Échec de l'enregistrement: {response.get('message')}")

def login_callback(response):
    """
    Fonction de rappel pour l'authentification.
    
    Args:
        response: Réponse du serveur
    """
    if response.get('status') == 'success':
        logger.info(f"Authentification réussie! Manager ID: {response.get('manager_id')}")
        logger.info(f"Token: {response.get('token')}")
        logger.info(f"Refresh Token: {response.get('refresh_token')}")
    else:
        logger.error(f"Échec de l'authentification: {response.get('message')}")

def main():
    """
    Fonction principale.
    """
    # Exemple d'enregistrement
    logger.info("Tentative d'enregistrement d'un nouveau manager...")
    success, response = register_manager(
        username="manager_example",
        email="manager@example.com",
        password="password123",
        callback=register_callback
    )
    
    if success:
        logger.info("Enregistrement réussi!")
    else:
        logger.error(f"Échec de l'enregistrement: {response.get('message')}")
        
        # Si le manager existe déjà, essayer de se connecter
        if "déjà utilisé" in response.get('message', ''):
            logger.info("Tentative de connexion...")
            success, response = login_manager(
                username="manager_example",
                password="password123",
                callback=login_callback
            )
            
            if success:
                logger.info("Connexion réussie!")
            else:
                logger.error(f"Échec de la connexion: {response.get('message')}")
    
    # Attendre un peu pour que les logs s'affichent
    time.sleep(1)

if __name__ == "__main__":
    main()
