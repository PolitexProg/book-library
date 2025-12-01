import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
USERNAME = "admin"
PASSWORD = "adminpassword"
EMAIL = "admin@example.com"

try:
    if not User.objects.filter(username=USERNAME).exists():
        print(f"Creating superuser {USERNAME}...")
        User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
        print(f"Superuser created. Username: {USERNAME}, Password: {PASSWORD}")
    else:
        print(f"Superuser {USERNAME} already exists. Resetting password...")
        u = User.objects.get(username=USERNAME)
        u.set_password(PASSWORD)
        u.save()
        print(f"Password updated. Username: {USERNAME}, Password: {PASSWORD}")
except Exception as e:
    print(f"Error: {e}")
