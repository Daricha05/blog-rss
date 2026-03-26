import markdown
from django import template
from django.utils.safestring import mark_safe
import bleach

register = template.Library()

# Liste des balises HTML autorisées
ALLOWED_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'hr',
    'strong', 'em', 'b', 'i', 'u',
    'a', 'img',
    'ul', 'ol', 'li',
    'blockquote', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'div', 'span'
]

# Attributs autorisés
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    '*': ['class'],
    'code': ['class'],
    'pre': ['class'],
}

@register.filter(name='markdown')
def render_markdown(text):
    """Convertit le markdown en HTML sécurisé"""
    if not text:
        return ''
    
    # Configuration des extensions markdown
    extensions = [
        'extra',           # Tables, abbr, etc.
        'codehilite',      # Coloration syntaxique
        'toc',            # Table des matières
        'nl2br',          # Newline to <br>
        'sane_lists',     # Listes plus intelligentes
    ]
    
    # Convertir markdown en HTML
    html = markdown.markdown(
        text,
        extensions=extensions,
        extension_configs={
            'codehilite': {
                'linenums': False,
                'guess_lang': True,
            }
        }
    )
    
    # Nettoyer le HTML pour éviter les injections XSS
    cleaned_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return mark_safe(cleaned_html)

@register.filter(name='markdown_preview')
def markdown_preview(text, words=50):
    """Affiche un aperçu markdown tronqué"""
    if not text:
        return ''
    
    # Convertir en HTML
    html = render_markdown(text)
    
    # Extraire le texte brut
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    plain_text = soup.get_text()
    
    # Tronquer
    truncated = ' '.join(plain_text.split()[:words])
    
    return truncated