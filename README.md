# 🎯 COORDINATOR APP - CENTRE DE CONTRÔLE DU CALCUL DISTRIBUÉ

---

## 📝 DESCRIPTION DU PROJET

Le **Coordinator App** est le **cerveau central** du système de calcul distribué volontaire. Il orchestre toutes les communications entre les managers et les volontaires, gère l'authentification, les tâches, et fournit une interface de supervision complète.

**Architecture** : **Coordinator** ↔ Manager ↔ Volontaire

**Rôle** : Point central de contrôle, authentification, routage des messages, supervision du réseau

---

## 🎯 OBJECTIFS

- **Objectif principal** : Servir de coordinateur central pour tout le réseau de calcul distribué
- **Problématique** : Besoin d'un point central pour coordonner managers et volontaires de manière sécurisée
- **Solution** : Application Django full-stack avec MongoDB, Redis, et proxy de sécurité

---

## 🧩 FONCTIONNALITÉS

### 🔐 AUTHENTIFICATION CENTRALISÉE
- Authentification des managers via Redis Pub/Sub
- Authentification des volontaires
- Gestion des tokens JWT
- Contrôle d'accès granulaire par canaux

### 📡 COMMUNICATION REDIS AVANCÉE
- **Proxy Redis sécurisé** avec contrôle d'accès
- Routage intelligent des messages
- Support WebSockets pour le temps réel
- Logging complet de tous les messages

### 🗄️ GESTION MONGODB
- Stockage persistant des managers et volontaires
- Gestion des workflows et tâches
- Historique complet des communications
- Sauvegarde automatique des métadonnées

### 📊 INTERFACE DE SUPERVISION
- **Dashboard React/Vite** avec Material-UI
- Monitoring en temps réel du réseau
- Visualisation des performances (Recharts)
- Gestion des utilisateurs et permissions

### 🛡️ SÉCURITÉ AVANCÉE
- Proxy Redis avec authentification JWT
- Filtrage des données sensibles
- Contrôle d'accès par rôles
- Audit trail complet

---

## 🚀 PRÉREQUIS SYSTÈME

### 🔧 **Logiciels Requis**
- **Python 3.8+** - [Télécharger Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Télécharger Node.js](https://nodejs.org/)
- **MongoDB 5.0+** - [Installer MongoDB](https://docs.mongodb.com/manual/installation/)
- **Redis Server 6.0+** - [Installer Redis](https://redis.io/docs/getting-started/installation/)
- **Git** - [Installer Git](https://git-scm.com/downloads)

### 🌐 **Configuration Réseau**
- **Port 8001** : Backend Django/ASGI (WebSockets)
- **Port 5173** : Frontend React/Vite (développement)
- **Port 6379** : Redis Server principal
- **Port 6380** : Proxy Redis sécurisé
- **Port 27017** : MongoDB

---

## 📦 INSTALLATION COMPLÈTE

### 1️⃣ **Cloner le Projet**
```bash
git clone <repository-url>
cd Coordinator-App
```

### 2️⃣ **Installation Backend (Django)**
```bash
cd coordinator_project

# Créer l'environnement virtuel
python -m venv coordinator-env

# Activer l'environnement virtuel
# Sur Linux/Mac :
source coordinator-env/bin/activate
# Sur Windows :
coordinator-env\Scripts\activate

# Installer les dépendances Python
pip install -r requirements.txt
```

### 3️⃣ **Installation Frontend (React)**
```bash
cd ../frontend

# Installer les dépendances Node.js
npm install
```

### 4️⃣ **Configuration MongoDB**
```bash
# Démarrer MongoDB
sudo systemctl start mongod  # Linux
# OU
brew services start mongodb-community  # macOS
# OU démarrer MongoDB depuis Windows Services

# Vérifier que MongoDB fonctionne
mongo --eval "db.adminCommand('ismaster')"
```

### 5️⃣ **Configuration Redis**
```bash
# Démarrer Redis
redis-server

# Dans un autre terminal, vérifier Redis
redis-cli ping
# Devrait retourner : PONG
```

### 6️⃣ **Migrations Django**
```bash
cd coordinator_project

# Activer l'environnement virtuel
source coordinator-env/bin/activate

# Appliquer les migrations
python manage.py makemigrations
python manage.py migrate
```

---

## ▶️ LANCEMENT DE L'APPLICATION

### 🚀 **Backend (4 terminaux requis)**

#### **Terminal 1 : Redis Server**
```bash
# Démarrer Redis sur le port par défaut
redis-server
```

#### **Terminal 2 : MongoDB**
```bash
# Vérifier que MongoDB est démarré
sudo systemctl status mongod
# OU
brew services list | grep mongodb
```

#### **Terminal 3 : Proxy Redis Sécurisé**
```bash
cd coordinator_project
source coordinator-env/bin/activate

# Démarrer le proxy Redis avec contrôle d'accès
python manage.py start_redis_proxy --redis-host localhost --redis-port 6379 --proxy-port 6380
```

#### **Terminal 4 : Backend Django/ASGI**
```bash
cd coordinator_project
source coordinator-env/bin/activate

# Lancer avec Daphne (ASGI pour WebSockets)
daphne coordinator_project.asgi:application -p 8001 -b 0.0.0.0
```

### 🖥️ **Frontend**

#### **Terminal 5 : Frontend React/Vite**
```bash
cd frontend

# Lancer le serveur de développement
npm run dev
```

### 🌐 **Accéder aux Applications**
- **Frontend (Dashboard)** : `http://localhost:5173`
- **Backend API** : `http://localhost:8001/api/`
- **Admin Django** : `http://localhost:8001/admin/`
- **Redis Direct** : `localhost:6379`
- **Proxy Redis** : `localhost:6380`

---

## ⚙️ CONFIGURATION

### 🔧 **Configuration Backend**
Modifier `coordinator_project/coordinator_project/settings.py` :

```python
# MongoDB Configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_NAME = 'coordinator_db'

# Redis Configuration
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0

# Proxy Redis
REDIS_PROXY_HOST = 'localhost'
REDIS_PROXY_PORT = 6380
USE_REDIS_PROXY = True

# CORS pour le frontend
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3000',
]
```

### 🌐 **Configuration Frontend**
Créer `frontend/src/config.js` :

```javascript
export const API_BASE_URL = 'http://localhost:8001/api';
export const WS_BASE_URL = 'ws://localhost:8001/ws';
```

### 🔒 **Configuration JWT**
```python
# settings.py
SECRET_KEY = 'your-secret-key-here'

# Redis JWT Configuration
JWT_EXPIRATION_HOURS = 24
JWT_REFRESH_EXPIRATION_HOURS = 168  # 7 jours
```

---

## 📁 STRUCTURE DU PROJET

```
Coordinator-App/
├── coordinator_project/         # Backend Django
│   ├── manage.py               # Point d'entrée Django
│   ├── requirements.txt        # Dépendances Python
│   ├── coordinator_project/    # Configuration Django
│   │   ├── settings.py        # Configuration principale
│   │   ├── urls.py            # Routes principales
│   │   ├── asgi.py            # Configuration ASGI
│   │   └── db.py              # Connexion MongoDB
│   ├── manager/               # App gestion managers
│   │   ├── models.py          # Modèles MongoDB
│   │   ├── views.py           # API REST managers
│   │   ├── serializers.py     # Sérialiseurs DRF
│   │   └── urls.py            # Routes managers
│   ├── volunteer/             # App gestion volontaires
│   │   ├── models.py          # Modèles MongoDB volontaires
│   │   ├── views.py           # API REST volontaires
│   │   └── serializers.py     # Sérialiseurs volontaires
│   ├── redis_communication/   # Communication Redis
│   │   ├── client.py          # Client Redis universel
│   │   ├── handlers.py        # Gestionnaires messages
│   │   ├── auth_client.py     # Client authentification
│   │   └── utils.py           # Utilitaires JWT
│   ├── communication/         # Proxy Redis sécurisé
│   │   ├── proxy.py           # Proxy avec contrôle d'accès
│   │   └── management/        # Commandes Django
│   └── message_logging/       # Logging des messages
└── frontend/                  # Frontend React
    ├── package.json           # Dépendances Node.js
    ├── vite.config.js         # Configuration Vite
    ├── src/
    │   ├── App.jsx            # Application principale
    │   ├── components/        # Composants React
    │   ├── pages/             # Pages de l'application
    │   └── services/          # Services API
    └── public/                # Assets statiques
```

---

## 🔄 FONCTIONNEMENT

### 1. **Démarrage du Coordinateur**
- MongoDB et Redis démarrent
- Le proxy Redis s'initialise avec les règles de sécurité
- Le backend Django/ASGI démarre avec WebSockets
- Le frontend React se connecte au backend

### 2. **Connexion des Managers**
- Manager s'authentifie via Redis Pub/Sub
- Le coordinateur vérifie les identifiants dans MongoDB
- Un token JWT est généré et renvoyé
- Le manager peut maintenant publier sur ses canaux autorisés

### 3. **Connexion des Volontaires**
- Processus similaire avec authentification spécifique
- Enregistrement des ressources système dans MongoDB
- Attribution d'un token avec permissions volontaire

### 4. **Routage des Messages**
- Tous les messages passent par le proxy Redis
- Vérification JWT et autorisation par canal
- Logging automatique dans MongoDB
- Transmission sécurisée aux destinataires

---

## 🛑 ARRÊTER L'APPLICATION

```bash
# Dans chaque terminal, appuyez sur :
Ctrl + C

# Arrêter MongoDB
sudo systemctl stop mongod  # Linux
brew services stop mongodb-community  # macOS

# Arrêter Redis
redis-cli shutdown

# Désactiver l'environnement virtuel
deactivate
```

---

## 🐛 DÉPANNAGE

### ❌ **Erreur de connexion MongoDB**
```bash
# Vérifier le statut de MongoDB
sudo systemctl status mongod

# Redémarrer MongoDB si nécessaire
sudo systemctl restart mongod

# Vérifier les logs
sudo tail -f /var/log/mongodb/mongod.log
```

### ❌ **Erreur de connexion Redis**
```bash
# Vérifier que Redis fonctionne
redis-cli ping

# Redémarrer Redis si nécessaire
sudo systemctl restart redis-server
```

### ❌ **Erreur de port occupé**
```bash
# Vérifier quels ports sont utilisés
netstat -tlnp | grep -E '(8001|5173|6379|6380|27017)'

# Tuer un processus si nécessaire
sudo kill -9 $(lsof -t -i:8001)
```

### ❌ **Problème CORS Frontend**
Vérifier que le backend est configuré pour accepter le frontend :
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Port Vite
]
```

---

## 📊 MONITORING

### 📈 **Tableau de Bord**
- **URL** : `http://localhost:5173`
- **Fonctionnalités** :
  - Vue d'ensemble du réseau
  - Status des managers et volontaires
  - Performances des tâches
  - Logs temps réel

### 📋 **Commandes de Surveillance**
```bash
# Logs du coordinateur
tail -f coordinator_project/COORDINATOR.LOG

# Status MongoDB
mongo --eval "db.stats()"

# Status Redis
redis-cli info

# Connexions actives
redis-cli client list
```

### 🔍 **API de Monitoring**
```bash
# Health check du système
curl http://localhost:8001/api/system-health/

# Statistiques des volontaires
curl http://localhost:8001/api/analytics/volunteers_by_status/

# Performance des tâches
curl http://localhost:8001/api/analytics/task_performance/
```

---

## 🔧 COMMANDES UTILES

### 📊 **Gestion MongoDB**
```bash
# Accéder à la base de données
mongo coordinator_db

# Voir les collections
show collections

# Voir les managers
db.manager.find().pretty()

# Voir les volontaires
db.volunteer.find().pretty()
```

### 📡 **Gestion Redis**
```bash
# Voir tous les canaux actifs
redis-cli pubsub channels

# Monitorer les messages
redis-cli monitor

# Voir les clients connectés
redis-cli client list
```

### 🐛 **Debug**
```bash
# Démarrer avec logs détaillés
cd coordinator_project
python manage.py runserver --verbosity=2

# Test du proxy Redis
cd coordinator_project
python manage.py start_redis_proxy --redis-host localhost --redis-port 6379 --proxy-port 6380
```

---

## 📄 LICENCE

Ce projet est **open source** sous licence MIT.  
Réutilisation, modification et contribution autorisées.

---

## 👥 CONTRIBUTEURS

- **Équipe Coordinator** - Développement du système central
- **Équipe Manager** - Intégration des workflows
- **Équipe Volunteer** - Communication distribuée

---

## 📞 SUPPORT

En cas de problème :

1. **Vérifier les prérequis** : MongoDB, Redis, Python, Node.js
2. **Consulter les logs** : `COORDINATOR.LOG`, `mongod.log`
3. **Tester les connexions** : MongoDB (27017), Redis (6379), Proxy (6380)
4. **Vérifier les ports** : Backend (8001), Frontend (5173)
5. **Contacter l'équipe** si le problème persiste

### 🔗 **Liens Utiles**
- Documentation MongoDB : https://docs.mongodb.com/
- Documentation Redis : https://redis.io/documentation
- Documentation Django : https://docs.djangoproject.com/
- Documentation React : https://reactjs.org/docs/

---