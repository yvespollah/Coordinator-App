"""
Consumers WebSocket pour la communication en temps réel avec Redis.
Ce module permet aux clients frontend de se connecter via WebSocket
et d'interagir avec les canaux Redis.
"""

import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
import redis.asyncio as aioredis
from .models import ConnectionState
import logging

logger = logging.getLogger(__name__)

class RedisConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket pour la communication avec Redis.
    Permet aux clients frontend de s'abonner aux canaux Redis
    et de publier des messages.
    """
    
    async def connect(self):
        """Établit la connexion WebSocket et initialise Redis"""
        # Récupérer le token et le type depuis les paramètres de requête
        self.token = self.scope['url_route']['kwargs'].get('token', '')
        self.client_type = self.scope.get('query_string', b'').decode().split('&')
        self.client_type = dict(item.split('=') for item in self.client_type if '=' in item).get('type', 'unknown')
        
        # Valider le token (à implémenter)
        is_valid = await self.validate_token(self.token, self.client_type)
        
        if not is_valid:
            logger.warning(f"Invalid token: {self.token} for {self.client_type}")
            await self.close(code=4001)
            return
        
        # Accepter la connexion
        await self.accept()
        
        # Initialiser Redis
        self.redis = await aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        
        # Stocker les abonnements
        self.subscriptions = set()
        self.pubsub = self.redis.pubsub()
        
        # Envoyer un message de confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'client_id': self.client_id,
            'client_type': self.client_type
        }))
        
        # Démarrer la tâche d'écoute Redis
        self.redis_listener_task = asyncio.create_task(self.redis_listener())
        
        logger.info(f"WebSocket connected: {self.client_id} ({self.client_type})")

    async def disconnect(self, close_code):
        """Ferme la connexion et nettoie les ressources"""
        # Annuler la tâche d'écoute
        if hasattr(self, 'redis_listener_task'):
            self.redis_listener_task.cancel()
            
        # Se désabonner de tous les canaux
        if hasattr(self, 'pubsub') and self.pubsub:
            for channel in self.subscriptions:
                await self.pubsub.unsubscribe(channel)
            await self.pubsub.close()
            
        # Fermer la connexion Redis
        if hasattr(self, 'redis') and self.redis:
            await self.redis.close()
            
        # Mettre à jour l'état de connexion
        if hasattr(self, 'client_id'):
            await self.update_connection_state(False)
            
        logger.info(f"WebSocket disconnected: {getattr(self, 'client_id', 'unknown')}")

    async def receive(self, text_data):
        """Reçoit un message du client WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'subscribe':
                await self.handle_subscribe(data)
            elif action == 'unsubscribe':
                await self.handle_unsubscribe(data)
            elif action == 'publish':
                await self.handle_publish(data)
            else:
                logger.warning(f"Unknown action: {action}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f"Unknown action: {action}"
                }))
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {text_data}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': "Invalid JSON"
            }))
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def handle_subscribe(self, data):
        """Gère l'abonnement à un canal Redis"""
        channel = data.get('channel')
        if not channel:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': "Channel is required"
            }))
            return
            
        # S'abonner au canal
        await self.pubsub.subscribe(channel)
        self.subscriptions.add(channel)
        
        await self.send(text_data=json.dumps({
            'type': 'subscribed',
            'channel': channel
        }))
        
        logger.info(f"Client {self.client_id} subscribed to {channel}")

    async def handle_unsubscribe(self, data):
        """Gère le désabonnement d'un canal Redis"""
        channel = data.get('channel')
        if not channel:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': "Channel is required"
            }))
            return
            
        # Se désabonner du canal
        if channel in self.subscriptions:
            await self.pubsub.unsubscribe(channel)
            self.subscriptions.remove(channel)
            
            await self.send(text_data=json.dumps({
                'type': 'unsubscribed',
                'channel': channel
            }))
            
            logger.info(f"Client {self.client_id} unsubscribed from {channel}")

    async def handle_publish(self, data):
        """Gère la publication d'un message sur un canal Redis"""
        channel = data.get('channel')
        message = data.get('data')
        
        if not channel or message is None:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': "Channel and data are required"
            }))
            return
            
        # Publier le message
        await self.redis.publish(channel, json.dumps(message))
        
        await self.send(text_data=json.dumps({
            'type': 'published',
            'channel': channel
        }))
        
        logger.info(f"Client {self.client_id} published to {channel}")

    async def redis_listener(self):
        """Écoute les messages Redis et les transmet au client WebSocket"""
        try:
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    channel = message['channel']
                    try:
                        data = json.loads(message['data'])
                        await self.send(text_data=json.dumps({
                            'type': 'message',
                            'channel': channel,
                            'data': data
                        }))
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from Redis: {message['data']}")
                        
                # Courte pause pour éviter de surcharger la CPU
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            # Tâche annulée, c'est normal lors de la déconnexion
            pass
        except Exception as e:
            logger.exception(f"Error in Redis listener: {e}")

    @database_sync_to_async
    def validate_token(self, token, client_type):
        """
        Valide le token et récupère l'ID client.
        À remplacer par une vraie validation de token.
        """
        try:
            # Pour le développement, accepter tous les tokens
            # En production, vérifier dans la base de données
            if token == 'temp_token':
                # Token temporaire pour les tests
                self.client_id = f"{client_type}_temp"
                return True
                
            # Vérifier dans la base de données
            connection = ConnectionState.objects.filter(
                token=token,
                type=client_type
            ).first()
            
            if connection:
                self.client_id = connection.id
                return True
            return False
            
        except Exception as e:
            logger.exception(f"Error validating token: {e}")
            return False

    @database_sync_to_async
    def update_connection_state(self, is_connected):
        """Met à jour l'état de connexion dans la base de données"""
        try:
            connection = ConnectionState.objects.filter(id=self.client_id).first()
            if connection:
                connection.is_connected = is_connected
                connection.save()
                logger.info(f"Updated connection state for {self.client_id}: {is_connected}")
        except Exception as e:
            logger.exception(f"Error updating connection state: {e}")
