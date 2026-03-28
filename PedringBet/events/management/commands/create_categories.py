from django.core.management.base import BaseCommand
from events.models import Category


class Command(BaseCommand):
    help = 'Create default categories for betting events'

    def handle(self, *args, **options):
        default_categories = [
            {'name': 'Sports', 'description': 'Sports events and matches'},
            {'name': 'Football', 'description': 'Football and soccer matches'},
            {'name': 'Basketball', 'description': 'Basketball games'},
            {'name': 'Tennis', 'description': 'Tennis tournaments and matches'},
            {'name': 'Horse Racing', 'description': 'Horse racing events'},
            {'name': 'Esports', 'description': 'Esports tournaments'},
            {'name': 'Politics', 'description': 'Political events and elections'},
            {'name': 'Entertainment', 'description': 'Entertainment events and awards'},
        ]

        created_count = 0
        for cat_data in default_categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nCreated {created_count} new categories')
        )
