from django.core.management.base import BaseCommand
from geopy.geocoders import Nominatim
from agmp_app.models import VariantStudyagmp # Update with your model's actual import

class Command(BaseCommand):
    help = 'Generate coordinates from country names and update them in the database'

    def handle(self, *args, **options):
        geolocator = Nominatim(user_agent='agmp_app')  # Replace 'your_app_name' with a unique identifier

        rows = VariantStudyagmp.objects.all()  # Retrieve all rows from your table

        for row in rows:
            country_name = row.country_participant  # Replace with the actual field name storing country names
            if country_name:
                location = geolocator.geocode(country_name)
                if location:
                    row.latitude = location.latitude
                    row.longitude = location.longitude
                    row.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully generated coordinates for {country_name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Could not generate coordinates for {country_name}'))
            else:
                self.stdout.write(self.style.WARNING('Country name missing in this row'))
        self.stdout.write(self.style.SUCCESS('Coordinates generation completed'))
         