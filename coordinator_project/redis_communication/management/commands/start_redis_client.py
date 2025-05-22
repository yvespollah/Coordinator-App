"""
Commande Django pour démarrer le client Redis.
"""

from django.core.management.base import BaseCommand
import logging
import time
from redis_communication.client import RedisClient

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Démarre le client Redis pour la communication'

    def add_arguments(self, parser):
        parser.add_argument(
            '--retry',
            type=int,
            default=5,
            help='Nombre de tentatives de connexion (défaut: 5)'
        )
        parser.add_argument(
            '--retry-delay',
            type=int,
            default=2,
            help='Délai entre les tentatives en secondes (défaut: 2)'
        )

    def handle(self, *args, **options):
        retry_count = options['retry']
        retry_delay = options['retry_delay']
        
        self.stdout.write(self.style.SUCCESS(
            f'Démarrage du client Redis (tentatives: {retry_count}, délai: {retry_delay}s)'
        ))
        
        # Récupérer l'instance du client
        client = RedisClient.get_instance()
        
        # Tentatives de démarrage
        for attempt in range(1, retry_count + 1):
            self.stdout.write(f'Tentative {attempt}/{retry_count}...')
            
            if client.start():
                self.stdout.write(self.style.SUCCESS(
                    f'Client Redis démarré avec succès!'
                ))
                
                # Afficher les canaux auxquels le client est abonné
                channels = list(client.handlers.keys())
                self.stdout.write(f'Abonné à {len(channels)} canaux:')
                for channel in channels:
                    self.stdout.write(f'  - {channel}')
                
                return
            
            if attempt < retry_count:
                self.stdout.write(self.style.WARNING(
                    f'Échec de la connexion. Nouvelle tentative dans {retry_delay} secondes...'
                ))
                time.sleep(retry_delay)
        
        self.stdout.write(self.style.ERROR(
            f'Impossible de démarrer le client Redis après {retry_count} tentatives'
        ))
        self.stdout.write(self.style.WARNING(
            'Assurez-vous que le proxy Redis est démarré avec la commande:'
        ))
        self.stdout.write(self.style.WARNING(
            '  python manage.py start_redis_proxy'
        ))
