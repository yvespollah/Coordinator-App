"""
Exemple d'utilisation des fonctions d'authentification pour les volontaires.
"""

import logging
import sys
import os
import time
import platform
import psutil
import uuid
import socket

# Ajouter le répertoire parent au chemin de recherche pour pouvoir importer redis_communication
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from redis_communication.auth_client import register_volunteer, login_volunteer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_system_info():
    """
    Récupère les informations système du volontaire.
    
    Returns:
        dict: Informations système
    """
    try:
        # Récupérer l'adresse IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except:
        ip_address = "127.0.0.1"
    
    return {
        'cpu_model': platform.processor() or "Unknown CPU",
        'cpu_cores': psutil.cpu_count(logical=True),
        'total_ram': int(psutil.virtual_memory().total / (1024 * 1024)),  # En MB
        'available_storage': int(psutil.disk_usage('/').free / (1024 * 1024 * 1024)),  # En GB
        'operating_system': f"{platform.system()} {platform.release()}",
        'gpu_available': False,  # À modifier si une GPU est disponible
        'gpu_model': None,
        'gpu_memory': None,
        'ip_address': ip_address,
        'communication_port': 8000  # Port par défaut
    }

def register_callback(response):
    """
    Fonction de rappel pour l'enregistrement.
    
    Args:
        response: Réponse du serveur
    """
    if response.get('status') == 'success':
        logger.info(f"Enregistrement réussi! Volunteer ID: {response.get('volunteer_id')}")
        logger.info(f"Username: {response.get('username')}")
        logger.info(f"Password: {response.get('password')}")
        
        # Sauvegarder les identifiants pour une utilisation future
        with open("volunteer_credentials.txt", "w") as f:
            f.write(f"username={response.get('username')}\n")
            f.write(f"password={response.get('password')}\n")
            f.write(f"volunteer_id={response.get('volunteer_id')}\n")
    else:
        logger.error(f"Échec de l'enregistrement: {response.get('message')}")

def login_callback(response):
    """
    Fonction de rappel pour l'authentification.
    
    Args:
        response: Réponse du serveur
    """
    if response.get('status') == 'success':
        logger.info(f"Authentification réussie! Volunteer ID: {response.get('volunteer_id')}")
        logger.info(f"Token: {response.get('token')}")
        logger.info(f"Refresh Token: {response.get('refresh_token')}")
        
        # Sauvegarder le token pour une utilisation future
        with open("volunteer_token.txt", "w") as f:
            f.write(f"token={response.get('token')}\n")
            f.write(f"refresh_token={response.get('refresh_token')}\n")
    else:
        logger.error(f"Échec de l'authentification: {response.get('message')}")

def main():
    """
    Fonction principale.
    """
    # Générer un nom et un ID pour le volontaire
    hostname = platform.node()
    node_id = str(uuid.uuid4())[:8]
    
    # Récupérer les informations système
    system_info = get_system_info()
    
    # Vérifier si des identifiants existent déjà
    if os.path.exists("volunteer_credentials.txt"):
        logger.info("Identifiants trouvés, tentative de connexion...")
        
        # Charger les identifiants
        username = None
        password = None
        with open("volunteer_credentials.txt", "r") as f:
            for line in f:
                if line.startswith("username="):
                    username = line.strip().split("=")[1]
                elif line.startswith("password="):
                    password = line.strip().split("=")[1]
        
        if username and password:
            # Tenter de se connecter
            success, response = login_volunteer(
                username=username,
                password=password,
                callback=login_callback
            )
            
            if success:
                logger.info("Connexion réussie!")
                return
            else:
                logger.error(f"Échec de la connexion: {response.get('message')}")
                logger.info("Tentative d'enregistrement...")
        else:
            logger.error("Identifiants incomplets, tentative d'enregistrement...")
    else:
        logger.info("Aucun identifiant trouvé, tentative d'enregistrement...")
    
    # Tenter de s'enregistrer
    success, response = register_volunteer(
        name=hostname,
        node_id=node_id,
        system_info=system_info,
        callback=register_callback
    )
    
    if success:
        logger.info("Enregistrement réussi!")
        
        # Récupérer les identifiants
        username = response.get('username')
        password = response.get('password')
        
        # Tenter de se connecter
        logger.info("Tentative de connexion...")
        success, response = login_volunteer(
            username=username,
            password=password,
            callback=login_callback
        )
        
        if success:
            logger.info("Connexion réussie!")
        else:
            logger.error(f"Échec de la connexion: {response.get('message')}")
    else:
        logger.error(f"Échec de l'enregistrement: {response.get('message')}")
    
    # Attendre un peu pour que les logs s'affichent
    time.sleep(1)

if __name__ == "__main__":
    main()
