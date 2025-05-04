"""
Configuration des URLs pour le module de communication.
Ce fichier définit les points d'entrée de l'API REST.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Création d'un routeur vide pour éviter l'erreur
router = DefaultRouter()

# Définir une liste vide de patterns d'URL
urlpatterns = []

# Ajouter les URLs du routeur
urlpatterns += router.urls