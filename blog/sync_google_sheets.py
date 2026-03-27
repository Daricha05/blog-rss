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

    def extract_image_url(self, raw_data):
        """
        Extrait l'URL de l'image depuis différents formats :
        - URL directe: https://exemple.com/image.jpg
        - Balise img: <img src="https://exemple.com/image.jpg">
        - Balise a avec img: <a href="..."><img src="https://exemple.com/image.jpg"></a>
        """
        if not raw_data:
            return ''
        
        # Cas 1: Déjà une URL directe
        if raw_data.startswith('http://') or raw_data.startswith('https://'):
            # Vérifier si c'est une URL d'image directe
            if any(raw_data.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                return raw_data
            
        # Cas 2: Extraire de la balise img (plusieurs patterns)
        patterns = [
            r'<img[^>]+src="([^">]+)"',           # src avec guillemets
            r"<img[^>]+src='([^'>]+)'",           # src avec apostrophes
            r'<img[^>]+src=([^\s>]+)',            # src sans guillemets
        ]
        
        for pattern in patterns:
            img_match = re.search(pattern, raw_data)
            if img_match:
                url = img_match.group(1)
                # Nettoyer l'URL
                url = url.strip()
                if url and (url.startswith('http://') or url.startswith('https://')):
                    return self.clean_url_length(url)
        
        # Cas 3: Chercher dans les balises a contenant des img
        a_img_match = re.search(r'<a[^>]*>.*?<img[^>]+src="([^">]+)".*?</a>', raw_data, re.DOTALL)
        if a_img_match:
            url = a_img_match.group(1).strip()
            if url.startswith('http://') or url.startswith('https://'):
                return self.clean_url_length(url)
        
        # Cas 4: Chercher n'importe quelle URL dans le texte
        url_match = re.search(r'https?://[^\s<>"\']+\.(?:jpg|jpeg|png|gif|webp|svg)', raw_data, re.IGNORECASE)
        if url_match:
            return self.clean_url_length(url_match.group(0))
        
        return ''

    def clean_url_length(self, url):
        """Limite la longueur de l'URL à 500 caractères"""
        if len(url) > 500:
            try:
                parsed = urlparse(url)
                # Garder seulement l'essentiel
                clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                url = clean[:500]
            except:
                url = url[:500]
        return url

    def clean_slug(self, title):
        """Génère un slug court"""
        if not title:
            return ''
        
        # Limiter le titre pour le slug
        short_title = title[:100]
        slug = slugify(short_title)
        
        # Tronquer à 50 caractères
        slug = slug[:50]
        
        # Supprimer les tirets en début/fin
        slug = slug.strip('-')
        
        return slug
    
    def clean_content(self, content):
        """Nettoie le contenu HTML en supprimant les balises a autour des images"""
        if not content:
            return ''
        
        # Supprimer les balises a qui contiennent des images
        cleaned = re.sub(r'<a[^>]*>\s*<img([^>]+)>\s*</a>', r'<img\1>', content)
        
        return cleaned
    
    def handle(self, *args, **options):
        try:
            # Chercher credentials.json dans plusieurs endroits possibles
            possible_paths = [
                'credentials.json',
                'blog/credentials.json',
                os.path.join(os.path.dirname(__file__), '../../credentials.json'),
                os.path.join(os.path.dirname(__file__), '../credentials.json'),
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
                    
                    # Extraire et nettoyer l'URL de l'image
                    raw_image = record.get('URL Image', '')
                    image_url = self.extract_image_url(raw_image)
                    
                    # Nettoyer le contenu (supprimer les balises a autour des images)
                    clean_content = self.clean_content(content)
                    
                    # Générer un slug court
                    slug = self.clean_slug(title)
                    
                    if not title or not clean_content:
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
                    
                    # Vérifier l'unicité du slug
                    original_slug = slug
                    counter = 1
                    unique_slug = slug
                    while RSSArticle.objects.filter(slug=unique_slug).exists():
                        suffix = f"-{counter}"
                        unique_slug = f"{original_slug[:50-len(suffix)]}{suffix}"
                        counter += 1
                    
                    # Vérifier si l'article existe
                    existing = RSSArticle.objects.filter(title=title).first()
                    
                    if existing:
                        existing.date = article_date
                        existing.suggested_post = clean_content
                        existing.image_url = image_url
                        existing.save()
                        articles_updated += 1
                        self.stdout.write(f"Updated: {title[:50]}...")
                    else:
                        article = RSSArticle(
                            date=article_date,
                            title=title,
                            slug=unique_slug,
                            suggested_post=clean_content,
                            image_url=image_url,
                            published=False
                        )
                        article.save()
                        articles_created += 1
                        self.stdout.write(f"Created: {title[:50]}...")
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Row {idx}: Error - {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Sync completed: {articles_created} created, {articles_updated} updated'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Fatal error: {str(e)}'))