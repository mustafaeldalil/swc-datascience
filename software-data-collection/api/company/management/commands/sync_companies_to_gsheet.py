from django.core.management.base import BaseCommand, CommandError

from company.tasks import sync_companies_to_gsheet

class Command(BaseCommand):
    help = "sync companies to gsheet"

    def handle(self, *args, **options):
        rows = sync_companies_to_gsheet()
        print(rows)