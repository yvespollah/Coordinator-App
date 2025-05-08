"""
Commande Django pour démarrer le service de communication.
Ce service écoute les canaux Redis et traite les messages entrants.
"""

from django.core.management.base import BaseCommand
import time
import logging
import signal
import sys
from communication.consumers import communication_service

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Démarre le service de communication qui écoute les canaux Redis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Exécuter en arrière-plan'
        )

    def handle(self, *args, **options):
        daemon = options['daemon']
        
        self.stdout.write(self.style.SUCCESS(
            'Démarrage du service de communication...'
        ))
        
        # Configurer le gestionnaire de signaux pour arrêter proprement le service
        def signal_handler(sig, frame):
            self.stdout.write(self.style.WARNING(
                'Arrêt du service de communication...'
            ))
            communication_service.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Démarrer le service
            communication_service.start()
            
            self.stdout.write(self.style.SUCCESS(
                'Service de communication démarré avec succès'
            ))
            
            # Maintenir le processus en vie
            if not daemon:
                self.stdout.write(self.style.SUCCESS(
                    'Appuyez sur Ctrl+C pour arrêter le service'
                ))
                
                while True:
                    time.sleep(1)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Erreur lors du démarrage du service: {e}'
            ))
            communication_service.stop()
            sys.exit(1)
