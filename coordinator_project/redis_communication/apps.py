"""
Configuration de l'application Django pour le module de communication Redis.
"""

from django.apps import AppConfig
import logging
import threading
import time
import os

logger = logging.getLogger(__name__)

class RedisCommunicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'redis_communication'
    verbose_name = 'Communication Redis Universelle'
    
    def ready(self):
        """
        Méthode appelée au démarrage de l'application Django.
        Initialise le client Redis et tente de le démarrer automatiquement.
        """
        # Ne pas exécuter en mode commande (sauf pour runserver)
        import sys
        if 'runserver' not in sys.argv and 'manage.py' in sys.argv[0]:
            return
            
        # Éviter les doubles chargements avec le reloader Django
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        # Importer ici pour éviter les imports circulaires
        from .client import RedisClient
        from .channels import register_handlers
        
        # Initialiser le client Redis
        client = RedisClient.get_instance()
        
        # Enregistrer les gestionnaires d'événements
        register_handlers(client)
        
        # Enregistrer les gestionnaires de performances des volontaires
        try:
            from .volunteer_performance_handlers import register_handlers as register_performance_handlers
            register_performance_handlers()
            logger.info("Gestionnaires de performances des volontaires enregistrés")
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des gestionnaires de performances: {e}")
        
        # Enregistrer les gestionnaires de demandes de réassignation de tâches
        try:
            from .task_assignment_handlers import register_handlers as register_task_assignment_handlers
            register_task_assignment_handlers()
            logger.info("Gestionnaires de demandes de réassignation de tâches enregistrés")
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des gestionnaires de demandes de réassignation de tâches: {e}")
        
        logger.info("Application redis_communication initialisée")
        logger.info(f"Canaux enregistrés: {list(client.handlers.keys())}")
        
        # Démarrer le client Redis dans un thread séparé
        def start_redis_client_with_retry():
            max_retries = 5
            retry_delay = 2
            
            logger.info(f"Tentative de démarrage automatique du client Redis (max: {max_retries} tentatives)")

            # Generer le JWT qui sera utililsé dans les publication du coordinateur
            from .utils import generate_token
            token = generate_token(str('COORDINATOR'), 'coordinator', 24)  # 24 heures

            # Stocker le token dans le fichier de .coordinator/redis_communication/token
            # Verfier que le dossier existe sinon le creer
            if not os.path.exists('.coordinator/redis_communication'):
                os.makedirs('.coordinator/redis_communication')
            
            with open('.coordinator/redis_communication/token', 'w') as f:
                f.write(token)
            
            logger.info(f"Token JWT généré et stocké dans le fichier .coordinator/redis_communication/token")            
            for attempt in range(1, max_retries + 1):
                logger.info(f"Tentative {attempt}/{max_retries}...")
                
                if client.start():
                    logger.info("Client Redis démarré automatiquement avec succès!")
                    return
                
                if attempt < max_retries:
                    logger.warning(f"Nouvelle tentative dans {retry_delay} secondes...")
                    time.sleep(retry_delay)
            
            logger.error("Impossible de démarrer automatiquement le client Redis")
            logger.warning("Utilisez 'python manage.py start_redis_client' pour démarrer manuellement")
        
        # Démarrer le thread après un court délai pour s'assurer que Django est complètement initialisé
        startup_thread = threading.Thread(target=lambda: (time.sleep(5), start_redis_client_with_retry()))
        startup_thread.daemon = True
        startup_thread.start()
        
        logger.info("Thread de démarrage automatique du client Redis lancé")
