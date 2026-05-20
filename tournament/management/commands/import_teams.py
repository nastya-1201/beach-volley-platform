import csv
from django.core.management.base import BaseCommand
from tournament.models import Team


class Command(BaseCommand):
    help = 'Импорт команд из CSV-файла'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV-файлу')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            created_count = 0
            updated_count = 0

            for row in reader:
                name = row.get('name', '').strip()
                city = row.get('city', '').strip()

                if not name:
                    self.stdout.write(self.style.WARNING('Пропущена строка без названия команды'))
                    continue

                team, created = Team.objects.update_or_create(
                    name=name,
                    defaults={'city': city}
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f'Импорт завершён. Создано: {created_count}, обновлено: {updated_count}'
            ))