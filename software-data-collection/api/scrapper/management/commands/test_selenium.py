from django.core.management.base import BaseCommand

from scrapper.selenium_initialization import initialize_selenium

class Command(BaseCommand):
    help = 'test if selenium is initialized'

    def handle(self, *args, **kwargs):
        driver = initialize_selenium()
        driver.get('http://www.saint-lo-agglo.fr')
        driver.close()
        print('OK NO ERROR')
