import os
from django.core.management.base import BaseCommand
from pathlib import Path

class Command(BaseCommand):
    help = 'Sync articles from Google Sheets'

    def handle(self, *args, **options):
        from blog.sync_google_sheets import Command as SyncCommand
        
        # Vérifier que le fichier credentials existe
        credentials_path = Path('credentials.json')
        if not credentials_path.exists():
            self.stdout.write(self.style.ERROR(
                'credentials.json not found! Please download it from Google Cloud Console.'
            ))
            return
        
        sync = SyncCommand()
        sync.handle(*args, **options)