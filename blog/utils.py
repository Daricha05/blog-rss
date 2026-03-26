import re
from urllib.parse import urlparse
from django.utils.text import slugify

def clean_image_url(url):
    """Nettoie et valide l'URL de l'image"""
    if not url:
        return ''
    
    # Extraire l'URL de l'image du code HTML si nécessaire
    img_match = re.search(r'<img[^>]+src="([^">]+)"', url)
    if img_match:
        url = img_match.group(1)
    
    # Nettoyer l'URL
    url = url.strip()
    
    # Vérifier que c'est une URL valide
    try:
        result = urlparse(url)
        if not result.scheme or not result.netloc:
            return ''
        
        # Limiter la longueur
        if len(url) > 500:
            # Essayer de supprimer les paramètres inutiles
            url = f"{result.scheme}://{result.netloc}{result.path}"
        
        return url[:500]
    except:
        return ''

def clean_content(content):
    """Nettoie le contenu HTML"""
    if not content:
        return ''
    
    # Supprimer les balises img pour éviter les doublons
    content = re.sub(r'<img[^>]+>', '', content)
    
    # Nettoyer le HTML
    return content.strip()

def generate_short_slug(title, max_length=50):
    """Génère un slug court"""
    if not title:
        return ''
    
    # Slugify et tronquer
    slug = slugify(title)
    slug = slug[:max_length]
    
    # Supprimer les tirets en début/fin
    slug = slug.strip('-')
    
    return slug