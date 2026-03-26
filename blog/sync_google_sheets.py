import re
from urllib.parse import urlparse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from blog.models import RSSArticle
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Sync articles from Google Sheets to Django'

    def clean_url(self, url):
        """Nettoie l'URL de l'image"""
        if not url:
            return ''
        
        # Si c'est du HTML avec img tag
        img_match = re.search(r'<img[^>]+src="([^">]+)"', url)
        if img_match:
            url = img_match.group(1)
        
        # Nettoyer
        url = url.strip()
        
        # Vérifier et limiter
        if len(url) > 500:
            # Extraire seulement l'URL de base sans paramètres
            parsed = urlparse(url)
            clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            url = clean if len(clean) <= 500 else clean[:500]
        
        return url

    def clean_slug(self, title):
        """Génère un slug court"""
        if not title:
            return ''
        
        # Limiter le titre pour le slug
        short_title = title[:100]  # Prendre seulement les 100 premiers caractères
        slug = slugify(short_title)
        
        # Tronquer à 50 caractères
        slug = slug[:50]
        
        # Supprimer les tirets en début/fin
        slug = slug.strip('-')
        
        return slug
    
    def handle(self, *args, **options):
        try:
            # Chercher credentials.json dans plusieurs endroits possibles
            possible_paths = [
                'credentials.json',  # racine du projet
                'blog/credentials.json',  # dans le dossier blog
                os.path.join(os.path.dirname(__file__), '../../credentials.json'),  # relatif à la commande
                os.path.join(os.path.dirname(__file__), '../credentials.json'),  # dans blog
            ]
            
            creds_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    creds_path = path
                    break
            
            if not creds_path:
                self.stdout.write(self.style.ERROR(
                    f'credentials.json not found! Searched in: {possible_paths}'
                ))
                return
            
            self.stdout.write(self.style.SUCCESS(f"Using credentials from: {creds_path}"))
            
            # Configuration Google Sheets
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
            client = gspread.authorize(creds)
            
            # ID de votre sheet
            sheet_id = '1hcSrBsBOfXs3Pc3RM7uqEFdn8rjJ1NSgB7uvFLsUkao'
            
            self.stdout.write(f"Opening sheet: {sheet_id}")
            
            # Ouvrir la sheet
            spreadsheet = client.open_by_key(sheet_id)
            sheet = spreadsheet.sheet1
            
            # Récupérer toutes les données
            records = sheet.get_all_records()
            
            self.stdout.write(f"Found {len(records)} rows in sheet")
            
            articles_created = 0
            articles_updated = 0
            
            for idx, record in enumerate(records, start=2):
                try:
                    title = record.get('Titre de l\'article', '')[:200]
                    content = record.get('Contenu', '')
                    date_str = record.get('Date', '')
                    
                    # Nettoyer l'URL de l'image
                    image_url = self.clean_url(record.get('URL Image', ''))
                    
                    # Générer un slug court
                    slug = self.clean_slug(title)
                    
                    # Vérifier l'unicité du slug
                    original_slug = slug
                    counter = 1
                    while RSSArticle.objects.filter(slug=slug).exists():
                        suffix = f"-{counter}"
                        slug = f"{original_slug[:50-len(suffix)]}{suffix}"
                        counter += 1
                    
                    if not title or not content:
                        self.stdout.write(self.style.WARNING(f"Row {idx}: Missing title or content, skipping"))
                        continue
                    
                    # Convertir la date
                    try:
                        if date_str:
                            if isinstance(date_str, str):
                                article_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            else:
                                article_date = date_str
                        else:
                            article_date = datetime.now().date()
                    except:
                        article_date = datetime.now().date()
                    
                    # Vérifier si l'article existe
                    existing = RSSArticle.objects.filter(title=title).first()
                    
                    if existing:
                        existing.date = article_date
                        existing.suggested_post = content
                        existing.image_url = image_url or ''
                        existing.save()
                        articles_updated += 1
                        self.stdout.write(f"Updated: {title}")
                    else:
                        article = RSSArticle(
                            date=article_date,
                            title=title,
                            slug=slugify(title),
                            suggested_post=content,
                            image_url=image_url or '',
                            published=False
                        )
                        article.save()
                        articles_created += 1
                        self.stdout.write(f"Created: {title}")
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Row {idx}: Error - {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Sync completed: {articles_created} created, {articles_updated} updated'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Fatal error: {str(e)}'))