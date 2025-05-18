"""
Vues API pour le module de communication.
Gère les requêtes HTTP et la coordination entre managers et volunteers.
"""

# Import minimal pour éviter les erreurs
from rest_framework import viewsets
from rest_framework.response import Response

# Classe vide pour éviter les erreurs
class CommunicationViewSet(viewsets.ViewSet):
    """
    Endpoints API pour la coordination.
    Les managers et volunteers utilisent leurs propres applications
    pour communiquer avec le coordinateur.
    """
    
    def list(self, request):
        """
        Liste tous les participants connectés.
        
        GET /communication/
        """
        return Response([])