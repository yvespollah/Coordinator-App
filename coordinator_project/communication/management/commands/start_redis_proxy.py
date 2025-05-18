"""
Commande Django pour démarrer le proxy Redis.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import threading
import logging
from communication.proxy import RedisProxy

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Démarre le proxy Redis pour contrôler les messages et souscriptions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--redis-host',
            default=getattr(settings, 'REDIS_HOST', 'localhost'),
            help='Hôte Redis (défaut: settings.REDIS_HOST ou localhost)'
        )
        parser.add_argument(
            '--redis-port',
            type=int,
            default=getattr(settings, 'REDIS_PORT', 6379),
            help='Port Redis (défaut: settings.REDIS_PORT ou 6379)'
        )
        parser.add_argument(
            '--proxy-port',
            type=int,
            default=6380,
            help='Port sur lequel le proxy écoute (défaut: 6380)'
        )
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Exécuter en arrière-plan'
        )

    def handle(self, *args, **options):
        redis_host = options['redis_host']
        redis_port = options['redis_port']
        proxy_port = options['proxy_port']
        daemon = options['daemon']
        
        self.stdout.write(self.style.SUCCESS(
            f'Démarrage du proxy Redis sur {redis_host}:{proxy_port} -> {redis_host}:{redis_port}'
        ))
        
        proxy = RedisProxy(
            redis_host=redis_host,
            redis_port=redis_port,
            proxy_port=proxy_port
        )
        
        if daemon:
            # Démarrer dans un thread séparé
            thread = threading.Thread(target=proxy.start)
            thread.daemon = True
            thread.start()
            
            self.stdout.write(self.style.SUCCESS(
                f'Proxy Redis démarré en arrière-plan (thread: {thread.name})'
            ))
            
            # Garder le processus principal en vie
            try:
                thread.join()
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Arrêt du proxy Redis...'))
        else:
            # Démarrer dans le processus principal
            try:
                proxy.start()
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Arrêt du proxy Redis...'))
            
        self.stdout.write(self.style.SUCCESS('Proxy Redis arrêté'))
