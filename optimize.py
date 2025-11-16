#!/usr/bin/env python
import os
import sys
import django

# اضافه کردن مسیر پروژه
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_py.settings')
django.setup()

from django.core.management import execute_from_command_line

def run_optimizations():
    """اجرای دستورات بهینه‌سازی"""
    commands = [
        ['manage.py', 'collectstatic', '--noinput'],
        ['manage.py', 'compress', '--force'],
        ['manage.py', 'createcachetable'],
    ]
    
    for command in commands:
        try:
            execute_from_command_line(command)
            print(f"✅ {command} executed successfully")
        except Exception as e:
            print(f"❌ Error in {command}: {e}")

if __name__ == '__main__':
    run_optimizations()