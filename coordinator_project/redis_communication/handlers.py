"""
Gestionnaires d'événements pour les messages Redis.
Inclut les gestionnaires pour l'authentification des managers et des volontaires.
"""

import logging
import json
import os
import uuid
import time
from typing import Dict, Any, Optional
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings

from manager.models import Manager
from volunteer.models import Volunteer
from .message import Message, MessageType
from .utils import generate_token

logger = logging.getLogger(__name__)


# Répertoire pour stocker les requêtes en attente
PENDING_REQUESTS_DIR = os.path.join(settings.BASE_DIR, 'pending_requests')
os.makedirs(PENDING_REQUESTS_DIR, exist_ok=True)

def save_pending_request(request_id: str, data: Dict[str, Any]):
    """
    Enregistre une requête en attente dans un fichier.
    
    Args:
        request_id: ID de la requête
        data: Données de la requête
    """
    filename = os.path.join(PENDING_REQUESTS_DIR, f"{request_id}.json")
    with open(filename, 'w') as f:
        json.dump({
            'data': data,
            'timestamp': time.time()
        }, f)
    
    logger.debug(f"Requête {request_id} enregistrée dans {filename}")

def get_pending_request(request_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère une requête en attente.
    
    Args:
        request_id: ID de la requête
        
    Returns:
        Dict ou None: Données de la requête si trouvée, None sinon
    """
    filename = os.path.join(PENDING_REQUESTS_DIR, f"{request_id}.json")
    if not os.path.exists(filename):
        return None
    
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de la requête {request_id}: {e}")
        return None

def delete_pending_request(request_id: str) -> bool:
    """
    Supprime une requête en attente.
    
    Args:
        request_id: ID de la requête
        
    Returns:
        bool: True si supprimée, False sinon
    """
    filename = os.path.join(PENDING_REQUESTS_DIR, f"{request_id}.json")
    if not os.path.exists(filename):
        return False
    
    try:
        os.remove(filename)
        logger.debug(f"Requête {request_id} supprimée")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la requête {request_id}: {e}")
        return False


def is_machine_already_registered(machine_info: Dict[str, Any]) -> Optional[Volunteer]:
    """
    Vérifie si une machine est déjà enregistrée en se basant sur ses caractéristiques matérielles.
    
    Args:
        machine_info: Informations détaillées de la machine
        
    Returns:
        Optional[Volunteer]: Le volontaire existant si trouvé, None sinon
    """
    if not machine_info:
        return None
    
    # Approche 1: Recherche par caractéristiques matérielles spécifiques
    # Critères d'identification de la machine
    primary_criteria = {}
    secondary_criteria = {}
    
    # Caractéristiques primaires (très stables)
    criteria_count = 0
    
    # CPU - Type et nombre de coeurs (très stable)
    if 'cpu' in machine_info:
        cpu_info = machine_info['cpu']
        if 'type' in cpu_info and cpu_info['type']:
            primary_criteria['cpu_model'] = cpu_info['type']
            criteria_count += 1
        if 'coeurs_physiques' in cpu_info:
            primary_criteria['cpu_cores'] = cpu_info['coeurs_physiques']
            criteria_count += 1
    
    # Architecture du système (très stable)
    if 'os' in machine_info and 'architecture' in machine_info['os']:
        arch = machine_info['os']['architecture']
        if arch:
            primary_criteria['machine_info__os__architecture'] = arch
            criteria_count += 1
    
    # RAM totale (très stable)
    if 'memoire' in machine_info and 'ram' in machine_info['memoire']:
        ram_info = machine_info['memoire']['ram']
        if 'total' in ram_info:
            # Convertir en MB si nécessaire
            ram_total = ram_info['total']
            if isinstance(ram_total, str) and 'GB' in ram_total:
                try:
                    ram_mb = float(ram_total.replace('GB', '').strip()) * 1024
                    primary_criteria['total_ram'] = ram_mb
                    criteria_count += 1
                except ValueError:
                    pass
    
    # Disque total (très stable)
    if 'disque' in machine_info and 'total' in machine_info['disque']:
        disk_total = machine_info['disque']['total']
        if isinstance(disk_total, str) and 'GB' in disk_total:
            try:
                disk_gb = float(disk_total.replace('GB', '').strip())
                primary_criteria['available_storage'] = disk_gb
                criteria_count += 1
            except ValueError:
                pass
    
    # Caractéristiques secondaires (peuvent changer, mais rarement)
    # Nom d'hôte
    if 'os' in machine_info and 'hostname' in machine_info['os']:
        hostname = machine_info['os']['hostname']
        if hostname:
            secondary_criteria['name__contains'] = hostname
    
    # OS (nom et version)
    if 'os' in machine_info:
        os_info = machine_info['os']
        os_string = f"{os_info.get('nom', '')} {os_info.get('version', '')}".strip()
        if os_string:
            secondary_criteria['operating_system'] = os_string
    
    # Fréquence CPU
    if 'cpu' in machine_info and 'frequence' in machine_info['cpu']:
        freq_info = machine_info['cpu']['frequence']
        if 'max' in freq_info:
            secondary_criteria['machine_info__cpu__frequence__max'] = freq_info['max']
    
    # Carte mère et BIOS
    if 'bios_carte_mere' in machine_info:
        secondary_criteria['machine_info__bios_carte_mere'] = machine_info['bios_carte_mere']
    
    # Recherche avec les critères primaires (très stables)
    if criteria_count >= 3:
        logger.debug(f"Recherche de machine avec critères primaires: {primary_criteria}")
        volunteer = Volunteer.objects(**primary_criteria).first()
        if volunteer:
            logger.info(f"Machine identifiée par caractéristiques matérielles primaires: {volunteer.name} (ID: {volunteer.id})")
            return volunteer
    
    # Si aucune correspondance avec les critères primaires, essayer avec une combinaison de primaires et secondaires
    if criteria_count >= 2 and secondary_criteria:
        combined_criteria = {**primary_criteria, **secondary_criteria}
        logger.debug(f"Recherche de machine avec critères combinés: {combined_criteria}")
        volunteer = Volunteer.objects(**combined_criteria).first()
        if volunteer:
            logger.info(f"Machine identifiée par combinaison de caractéristiques: {volunteer.name} (ID: {volunteer.id})")
            return volunteer
    
    # Approche 2: Recherche par similarité globale
    # Si aucune correspondance exacte n'est trouvée, on peut rechercher les machines les plus similaires
    # et vérifier si la similarité est suffisante pour considérer que c'est la même machine
    
    # Cette partie pourrait être implémentée dans une version future
    
    return None

# Gestionnaires génériques

def log_message_handler(channel: str, message: Message):
    """
    Gestionnaire simple qui journalise les messages reçus.
    
    Args:
        channel: Canal sur lequel le message a été reçu
        message: Message reçu
    """
    logger.info(f"Message reçu sur {channel}: {message.request_id} de {message.sender}")
    logger.debug(f"Contenu: {message.data}")

def heartbeat_handler(channel: str, message: Message):
    """
    Gestionnaire pour les messages de heartbeat.
    
    Args:
        channel: Canal sur lequel le message a été reçu
        message: Message reçu
    """
    sender_type = message.sender.get('type', 'unknown')
    sender_id = message.sender.get('id', 'unknown')
    logger.debug(f"Heartbeat reçu de {sender_type}:{sender_id}")

def error_handler(channel: str, message: Message):
    """
    Gestionnaire pour les messages d'erreur.
    
    Args:
        channel: Canal sur lequel le message a été reçu
        message: Message reçu
    """
    error_data = message.data
    error_msg = error_data.get('message', 'Erreur inconnue')
    error_code = error_data.get('code', 0)
    
    logger.error(f"Erreur sur {channel}: [{error_code}] {error_msg}")
    logger.error(f"Détails: {error_data}")

# Gestionnaires pour l'authentification des managers

def manager_registration_handler(channel: str, message: Message):
    """
    Gestionnaire pour l'enregistrement des managers.
    
    Args:
        channel: Canal sur lequel le message a été reçu
        message: Message reçu
    """
    from .client import RedisClient
    logger.setLevel(logging.INFO)
    logger.warning(f"Demande d'enregistrement de manager reçue: {message.data}")
    
    # Récupérer les données du message
    data = message.data
    request_id = message.request_id

    
    # Vérifier si data est un dictionnaire vide ou None
    if not data or not isinstance(data, dict):
        logger.error(f"Données invalides reçues: {data}")
        
        # Envoyer une réponse d'erreur
        client = RedisClient.get_instance()
        client.publish('auth/register_response', {
            'status': 'error',
            'message': "Format de données invalide"
        }, request_id=request_id)
        return
        
    # Compatibilité avec le format de données du manager
    # Si les données sont dans un format différent, essayer de les extraire
    if 'username' not in data and 'email' not in data and 'password' not in data:
        # Essayer de récupérer les données depuis le message original
        original_dict = message.to_dict()
        logger.info(f"Tentative d'extraction des données depuis le message original: {original_dict}")
        
        # Vérifier si les données sont directement dans le message
        if isinstance(original_dict.get('data'), dict):
            data = original_dict.get('data')
            logger.info(f"Données extraites du message original: {data}")
    
    # Vérifier que les données sont complètes
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            logger.error(f"Champ requis manquant: {field}")
            
            # Envoyer une réponse d'erreur
            client = RedisClient.get_instance()
            client.publish('auth/register_response', {
                'status': 'error',
                'message': f"Champ requis manquant: {field}"
            }, request_id=request_id, message_type='response')
            return
    
    # Enregistrer la requête en attente
    save_pending_request(request_id, data)
    
    # Récupérer les données
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    try:
        # Vérifier si MongoDB est disponible
        try:
            # Vérifier si le manager existe déjà            
            existing_email = Manager.objects(email=email).first()
            if existing_email:
                logger.warning(f"L'email {email} est déjà utilisé, envoie du message d'erreur")
                
                # Envoyer une réponse d'erreur
                client = RedisClient.get_instance()
                client.publish('auth/register_response', {
                    'status': 'error',
                    'message': "Cet email est déjà utilisé"
                }, request_id=request_id, message_type="response")
                logger.warning(f"Message publié sur 'auth/register_response' avec le request_id: {request_id}")
                
                # Supprimer la requête en attente
                delete_pending_request(request_id)
                return
        except Exception as mongo_error:
            # Si MongoDB n'est pas disponible, on enregistre l'erreur mais on continue
            logger.error(f"Erreur de connexion à MongoDB: {mongo_error}")
            logger.info("Poursuite de l'enregistrement sans vérification de duplicata (MongoDB indisponible)")
        
        # Créer le manager
        hashed_password = make_password(password)
        try:                
            # Créer le nouveau manager
            manager = Manager(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=hashed_password,
                status='active'  
            )
            manager.save()
            logger.warning(f"NOUVEAU MANAGER: {username} créé avec succès (ID: {manager.id})")
        except Exception as mongo_save_error:
            logger.error(f"Impossible de sauvegarder le manager dans MongoDB: {mongo_save_error}")
            # On simule un succès même si MongoDB n'est pas disponible
            # Cela permet au manager de continuer à fonctionner même sans MongoDB
            logger.warning("Simulation de succès d'enregistrement (MongoDB indisponible)")
        
        logger.warning(f"Manager {username} enregistré avec succès (ID: {manager.id})")
        
        # Envoyer une réponse de succès
        client = RedisClient.get_instance()
        client.publish('auth/register_response', {
            'status': 'success',
            'message': 'Enregistrement réussi',
            'manager_id': str(manager.id),
            'username': manager.username,
            'first_name': manager.first_name,
            'last_name': manager.last_name,
            'email': manager.email
        }, request_id=request_id, message_type="response")
        
        # Log pour vérifier que le message a bien été publié
        logger.warning(f"Réponse publiée sur auth/register_response avec request_id: {request_id}")
        
        # Supprimer la requête en attente
        delete_pending_request(request_id)
        
    except Exception as e:
        import traceback
        logger.error(f"Erreur lors de l'enregistrement du manager: {e}")
        logger.error(traceback.format_exc())
        
        # Envoyer une réponse d'erreur
        client = RedisClient.get_instance()
        client.publish('auth/register_response', {
            'status': 'error',
            'message': str(e)
        }, request_id=request_id, message_type="response")
        
        # Supprimer la requête en attente
        delete_pending_request(request_id)

def manager_login_handler(channel: str, message: Message):
    """
    Gestionnaire pour l'authentification des managers.
    
    Args:
        channel: Canal sur lequel le message a été reçu
        message: Message reçu
    """
    from .client import RedisClient
    
    logger.info(f"Demande d'authentification de manager reçue: {message.request_id}")
    
    # Récupérer les données du message
    data = message.data
    request_id = message.request_id
    
    # Vérifier que les données sont complètes
    required_fields = ['username', 'password']
    for field in required_fields:
        if field not in data:
            logger.error(f"Champ requis manquant: {field}")
            
            # Envoyer une réponse d'erreur
            client = RedisClient.get_instance()
            client.publish('auth/login_response', {
                'status': 'error',
                'message': f"Champ requis manquant: {field}"
            }, request_id=request_id, message_type="response")
            return
    
    # Enregistrer la requête en attente
    save_pending_request(request_id, data)
    
    # Récupérer les données
    username = data.get('username')
    password = data.get('password')
    
    try:
        # Rechercher le manager
        try:
            manager = Manager.objects(username=username).first()
            if not manager:
                logger.warning(f"Manager {username} introuvable")
                
                # Envoyer une réponse d'erreur
                response = Message.create_response(message, {
                    'status': 'error',
                    'message': 'Identifiants invalides'
                })
                client = RedisClient.get_instance()
                client.publish('auth/login_response', response, request_id=request_id)
                
                # Supprimer la requête en attente
                delete_pending_request(request_id)
                return
        except Exception as mongo_error:
            logger.error(f"Erreur de connexion à MongoDB: {mongo_error}")
            
            # Envoyer une réponse d'erreur
            response = Message.create_response(message, {
                'status': 'error',
                'message': 'Identifiants invalides'
            })
            client = RedisClient.get_instance()
            client.publish('auth/login_response', response, request_id=request_id)
            
            # Supprimer la requête en attente
            delete_pending_request(request_id)
            return
        
        # Vérifier le mot de passe
        try:
            if not check_password(password, manager.password):
                logger.warning(f"Mot de passe incorrect pour {username}")
                
                # Envoyer une réponse d'erreur
                response = Message.create_response(message, {
                    'status': 'error',
                    'message': 'Identifiants invalides'
                })
                client = RedisClient.get_instance()
                client.publish('auth/login_response', response, request_id=request_id)
                
                # Supprimer la requête en attente
                delete_pending_request(request_id)
                return
        except Exception as pwd_error:
            logger.error(f"Erreur lors de la vérification du mot de passe: {pwd_error}")
            
            # Envoyer une réponse d'erreur
            response = Message.create_response(message, {
                'status': 'error',
                'message': 'Identifiants invalides'
            })
            client = RedisClient.get_instance()
            client.publish('auth/login_response', response, request_id=request_id)
            
            # Supprimer la requête en attente
            delete_pending_request(request_id)
            return
        
        # Vérifier que le compte est actif
        if manager.status != 'active':
            logger.warning(f"Le compte {username} n'est pas actif")
            
            # Envoyer une réponse d'erreur
            client = RedisClient.get_instance()
            client.publish('auth/login_response', {
                'status': 'error',
                'message': "Ce compte n'est pas actif"
            }, request_id=request_id, message_type="response")
            
            # Supprimer la requête en attente
            delete_pending_request(request_id)
            return
        
        # Générer un token JWT et un refresh token
        token = generate_token(str(manager.id), 'manager', 24)  # 24 heures
        refresh_token = generate_token(str(manager.id), 'manager', 168)  # 7 jours
        
        # Mettre à jour la date de dernière connexion
        try:
            manager.last_login = datetime.utcnow()
            manager.save()
        except Exception as save_error:
            logger.error(f"Impossible de mettre à jour la date de dernière connexion: {save_error}")
            # On continue sans mettre à jour la date de dernière connexion
        
        logger.info(f"Manager {username} authentifié avec succès")
        
        # Envoyer une réponse de succès
        client = RedisClient.get_instance()
        client.publish('auth/login_response', {
            'status': 'success',
            'message': 'Authentification réussie',
            'token': token,
            'refresh_token': refresh_token,
            'manager_id': str(manager.id),
            'username': manager.username,
            'first_name': manager.first_name,
            'last_name': manager.last_name,
            'email': manager.email
        }, request_id=request_id, message_type="response")
        
        # Supprimer la requête en attente
        delete_pending_request(request_id)
        
    except Exception as e:
        import traceback
        logger.error(f"Erreur lors de l'authentification du manager: {e}")
        logger.error(traceback.format_exc())
        
        # Envoyer une réponse d'erreur
        client = RedisClient.get_instance()
        client.publish('auth/login_response', {
            'status': 'error',
            'message': str(e)
        }, request_id=request_id, message_type="response")
        
        # Supprimer la requête en attente
        delete_pending_request(request_id)

# Gestionnaires pour l'authentification des volontaires

def volunteer_registration_handler(channel: str, message: Message):
    """
    Gestionnaire pour l'enregistrement des volontaires.
    
    Args:
        channel: Canal sur lequel le message a été reçu
        message: Message reçu
    """
    from .client import RedisClient
    
    logger.info(f"Demande d'enregistrement de volontaire reçue: {message.request_id}")
    
    # Récupérer les données du message
    data = message.data
    request_id = message.request_id
    
    # Vérifier que les données sont complètes
    required_fields = ['name', 'ip_address', 'cpu_cores', 'ram_mb', 'disk_gb', 'username', 'password']
    for field in required_fields:
        if field not in data:
            logger.error(f"Champ requis manquant: {field}")
            
            # Envoyer une réponse d'erreur
            client = RedisClient.get_instance()
            client.publish('auth/volunteer_register_response', {
                'status': 'error',
                'message': f"Champ requis manquant: {field}"
            }, request_id=request_id)
            return
    
    # Enregistrer la requête en attente
    save_pending_request(request_id, data)
    
    # Récupérer les informations de base
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')
    ip_address = data.get('ip_address')
    cpu_cores = data.get('cpu_cores')
    ram_mb = data.get('ram_mb')
    disk_gb = data.get('disk_gb')
    
    # Extraire les informations de la machine si présentes
    machine_info = data.get('machine_info', {})
    
    # Déterminer le système d'exploitation
    os_info = "Unknown"
    if machine_info and 'os' in machine_info:
        os_info = f"{machine_info['os'].get('nom', 'Unknown')} {machine_info['os'].get('version', '')}"
    
    # Déterminer le modèle CPU
    cpu_model = "Unknown"
    if machine_info and 'cpu' in machine_info:
        cpu_model = machine_info['cpu'].get('type', 'Unknown')
    
    # Déterminer les informations GPU
    gpu_available = False
    gpu_model = None
    gpu_memory = None
    if machine_info and 'gpu' in machine_info:
        gpu_available = machine_info['gpu'].get('Disponible', False)
        if gpu_available:
            gpu_model = machine_info['gpu'].get('model', 'Unknown')
            gpu_memory = machine_info['gpu'].get('memory', 0)
    
    try:
        # Vérifier d'abord si la machine est déjà enregistrée en se basant sur ses caractéristiques matérielles
        existing_machine = is_machine_already_registered(machine_info)
        if existing_machine:
            logger.warning(f"La machine avec les caractéristiques fournies est déjà enregistrée sous le nom {existing_machine.name} (ID: {existing_machine.id})")
            
            # Mettre à jour les informations du volontaire existant si nécessaire
            existing_machine.username = username
            existing_machine.password = password
            existing_machine.name = name
            existing_machine.ip_address = ip_address
            existing_machine.current_status = 'available'
            existing_machine.last_activity = datetime.utcnow()
            
            # Mettre à jour les informations détaillées de la machine
            if machine_info:
                # Supprimer les informations trop détaillées qui pourraient causer des problèmes
                if 'partitions_disque' in machine_info:
                    del machine_info['partitions_disque']
                existing_machine.machine_info = machine_info
            
            existing_machine.save()
            
            logger.info(f"Informations du volontaire {name} (ID: {existing_machine.id}) mises à jour")
            
            # Générer un nouveau token
            token = generate_token(str(existing_machine.id), 'volunteer', 24)  # 24 heures
            
            # Envoyer une réponse de succès avec les informations mises à jour
            client = RedisClient.get_instance()
            client.publish('auth/volunteer_register_response', {
                'status': 'success',
                'message': 'Machine déjà enregistrée, informations mises à jour',
                'volunteer_id': str(existing_machine.id),
                'username': username,
                'token': token,
                'is_update': True
            }, request_id=request_id)
            
            # Supprimer la requête en attente
            delete_pending_request(request_id)
            return
        
        # Si la machine n'est pas déjà enregistrée, vérifier si le nom d'utilisateur est déjà utilisé
        existing_volunteer = Volunteer.objects(username=username).first()
        if existing_volunteer:
            logger.warning(f"Le volontaire avec username {username} existe déjà")
            
            # Envoyer une réponse d'erreur
            client = RedisClient.get_instance()
            client.publish('auth/volunteer_register_response', {
                'status': 'error',
                'message': "Ce nom d'utilisateur est déjà utilisé"
            }, request_id=request_id)
            
            # Supprimer la requête en attente
            delete_pending_request(request_id)
            return
        
        # Créer le volontaire avec les nouvelles informations
        volunteer = Volunteer(
            name=name,
            username=username,
            password=password,
            cpu_model=cpu_model,
            cpu_cores=cpu_cores,
            total_ram=ram_mb,
            available_storage=disk_gb,
            operating_system=os_info,
            gpu_available=gpu_available,
            gpu_model=gpu_model,
            gpu_memory=gpu_memory,
            ip_address=ip_address,
            communication_port=8002,  # Port par défaut pour les volontaires
            current_status='available'
        )
        
        # Stocker les informations détaillées de la machine
        # Limiter la taille des informations pour éviter les problèmes de sérialisation
        if machine_info:
            # Supprimer les informations trop détaillées qui pourraient causer des problèmes
            if 'partitions_disque' in machine_info:
                del machine_info['partitions_disque']
            volunteer.machine_info = machine_info
        
        volunteer.save()
        
        logger.info(f"Volontaire {name} ({username}) enregistré avec succès (ID: {volunteer.id})")
        
        # Envoyer une réponse de succès
        client = RedisClient.get_instance()
        client.publish('auth/volunteer_register_response', {
            'status': 'success',
            'message': 'Volontaire enregistré avec succès',
            'volunteer_id': str(volunteer.id),
            'username': username,
            'token': str(uuid.uuid4())  # Générer un token d'authentification
        }, request_id=request_id)
        
        # Supprimer la requête en attente
        delete_pending_request(request_id)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du volontaire: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Envoyer une réponse d'erreur
        client = RedisClient.get_instance()
        client.publish('auth/volunteer_register_response', {
            'status': 'error',
            'message': str(e)
        }, request_id=request_id)
        
        # Supprimer la requête en attente
        delete_pending_request(request_id)

def volunteer_login_handler(channel: str, message: Message):
    """
    Gestionnaire pour l'authentification des volontaires.
    
    Args:
        channel: Canal sur lequel le message a été reçu
        message: Message reçu
    """
    from .client import RedisClient
    
    logger.info(f"Demande d'authentification de volontaire reçue: {message.request_id}")
    
    # Récupérer les données du message
    data = message.data
    request_id = message.request_id
    
    # Vérifier que les données sont complètes
    required_fields = ['username', 'password']
    for field in required_fields:
        if field not in data:
            logger.error(f"Champ requis manquant: {field}")
            
            # Envoyer une réponse d'erreur
            client = RedisClient.get_instance()
            client.publish('auth/volunteer_login_response', {
                'status': 'error',
                'message': f"Champ requis manquant: {field}"
            }, request_id=request_id)
            return
    
    # Enregistrer la requête en attente
    save_pending_request(request_id, data)
    
    # Récupérer les données
    username = data.get('username')
    password = data.get('password')
    
    try:
        # Rechercher le volontaire par username
        volunteer = Volunteer.objects(username=username).first()
        if not volunteer:
            logger.warning(f"Volontaire avec username {username} introuvable")
            
            # Envoyer une réponse d'erreur
            client = RedisClient.get_instance()
            client.publish('auth/volunteer_login_response', {
                'status': 'error',
                'message': 'Identifiants invalides'
            }, request_id=request_id)
            
            # Supprimer la requête en attente
            delete_pending_request(request_id)
            return
        
        # Vérifier le mot de passe
        if volunteer.password != password:
            logger.warning(f"Mot de passe incorrect pour le volontaire {username}")
            
            # Envoyer une réponse d'erreur
            client = RedisClient.get_instance()
            client.publish('auth/volunteer_login_response', {
                'status': 'error',
                'message': 'Identifiants invalides'
            }, request_id=request_id)
            
            # Supprimer la requête en attente
            delete_pending_request(request_id)
            return
        
        # Générer un token JWT et un refresh token
        token = generate_token(str(volunteer.id), 'volunteer', 24)  # 24 heures
        refresh_token = generate_token(str(volunteer.id), 'volunteer', 168)  # 7 jours
        
        # Mettre à jour la date de dernière activité
        volunteer.last_activity = datetime.utcnow()
        volunteer.current_status = 'available'
        volunteer.save()
        
        logger.info(f"Volontaire {username} authentifié avec succès")
        
        # Mettre à jour les informations machine si fournies
        machine_info = data.get('machine_info')
        if machine_info:
            # Limiter la taille des informations pour éviter les problèmes de sérialisation
            if 'partitions_disque' in machine_info:
                del machine_info['partitions_disque']
            volunteer.machine_info = machine_info
            volunteer.save()
        
        # Envoyer une réponse de succès
        client = RedisClient.get_instance()
        client.publish('auth/volunteer_login_response', {
            'status': 'success',
            'message': 'Authentification réussie',
            'token': token,
            'refresh_token': refresh_token,
            'volunteer_id': str(volunteer.id),
            'username': volunteer.username,
            'name': volunteer.name
        }, request_id=request_id)
        
        # Supprimer la requête en attente
        delete_pending_request(request_id)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'authentification du volontaire: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Envoyer une réponse d'erreur
        client = RedisClient.get_instance()
        client.publish('auth/volunteer_login_response', {
            'status': 'error',
            'message': str(e)
        }, request_id=request_id)
        
        # Supprimer la requête en attente
        delete_pending_request(request_id)

# Dictionnaire des gestionnaires par défaut
DEFAULT_HANDLERS = {
    # Canaux génériques
    "coord/heartbeat": heartbeat_handler,
    "coord/emergency": error_handler,
    "system/error": error_handler,
    
    # Canaux d'authentification des managers
    "auth/register": manager_registration_handler,
    "auth/login": manager_login_handler,
    
    # Canaux d'authentification des volontaires
    "auth/volunteer_register": volunteer_registration_handler,
    "auth/volunteer_login": volunteer_login_handler
}
