from django.core.handlers.wsgi import WSGIHandler
from dj_static import Cling

application = WSGIHandler()
application = Cling(application)
