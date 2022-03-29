

import os

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Attendance_System.settings')

# application = get_wsgi_application()
application = DjangoWhiteNoise(get_wsgi_application())
