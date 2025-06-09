"""
Commande de gestion pour initialiser les performances des volontaires.
"""

import logging
from django.core.management.base import BaseCommand
from volunteer.models import Volunteer

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialise les performances des volontaires existants'

    def handle(self, *args, **options):
        """
        Exécute la commande pour initialiser les performances des volontaires.
        """
        self.stdout.write('Initialisation des performances des volontaires...')
        
        # Récupérer tous les volontaires
        volunteers = Volunteer.objects.all()
        count = 0
        
        for volunteer in volunteers:
            # Initialiser les performances si elles n'existent pas
            if not volunteer.performance or not isinstance(volunteer.performance, dict):
                volunteer.performance = {
                    'tasks_total': 0,
                    'tasks_completed': 0,
                    'tasks_failed': 0,
                    'trust_score': 0
                }
                volunteer.save()
                count += 1
                self.stdout.write(f'Performance initialisée pour le volontaire {volunteer.name}')
            else:
                # S'assurer que tous les champs nécessaires sont présents
                updated = False
                
                if 'tasks_total' not in volunteer.performance:
                    volunteer.performance['tasks_total'] = 0
                    updated = True
                    
                if 'tasks_completed' not in volunteer.performance:
                    volunteer.performance['tasks_completed'] = 0
                    updated = True
                    
                if 'tasks_failed' not in volunteer.performance:
                    volunteer.performance['tasks_failed'] = 0
                    updated = True
                    
                if 'trust_score' not in volunteer.performance:
                    volunteer.performance['trust_score'] = 0
                    updated = True
                
                if updated:
                    volunteer.save()
                    count += 1
                    self.stdout.write(f'Performance mise à jour pour le volontaire {volunteer.name}')
        
        self.stdout.write(self.style.SUCCESS(f'Performances initialisées pour {count} volontaires sur {volunteers.count()}'))
