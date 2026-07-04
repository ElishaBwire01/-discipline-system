from django.core.management.base import BaseCommand
from pathlib import Path
from datetime import datetime

class Command(BaseCommand):
    help = 'Show error logs from the error_logs.txt file'

    def add_arguments(self, parser):
        parser.add_argument('--tail', type=int, default=10, help='Number of recent errors to show')
        parser.add_argument('--clear', action='store_true', help='Clear the error log file')

    def handle(self, *args, **options):
        log_file = Path('error_logs.txt')
        
        if options['clear']:
            if log_file.exists():
                log_file.write_text('')
                self.stdout.write(self.style.SUCCESS('✅ Error log cleared!'))
            return
        
        if not log_file.exists():
            self.stdout.write(self.style.WARNING('⚠️ No error log found.'))
            return
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if not content.strip():
            self.stdout.write(self.style.SUCCESS('✅ No errors logged!'))
            return
        
        # Split by separators and get recent ones
        entries = content.split('=' * 80)
        recent = entries[-options['tail']:] if options['tail'] > 0 else entries
        
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write(f"📋 RECENT ERRORS (last {len(recent)} entries)")
        self.stdout.write(f"{'='*80}\n")
        
        for entry in recent:
            if entry.strip():
                self.stdout.write(entry.strip())
                self.stdout.write("\n" + "-"*80 + "\n")
