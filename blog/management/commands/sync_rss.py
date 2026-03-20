import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from blog.models import RSSArticle

class Command(BaseCommand):
    help = 'Synchroniser les articles depuis Google Sheets'

    def handle(self, *args, **kwargs):
        url_csv = "https://docs.google.com/spreadsheets/d/1nPagneBQmPxFrX24CATT8aVFRdGjj_qVLZNgE1h5BlQ/export?format=csv"

        try:
            df = pd.read_csv(url_csv)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur connexion Google Sheets: {e}"))
            return

        articles = df.to_dict(orient='records')

        for row in articles:
            try:
                date_value = datetime.strptime(row.get("date"), "%a, %d %b %Y %H:%M:%S %Z").date()
            except:
                date_value = datetime.today().date()

            RSSArticle.objects.update_or_create(
                title=row.get("Titre de l'article") or "Titre inconnu",
                defaults={
                    "date": date_value,
                    "suggested_post": row.get("Post LinkedIn suggéré") or "",
                    "published": True
                }
            )

        self.stdout.write(self.style.SUCCESS(f"{len(articles)} articles synchronisés !"))