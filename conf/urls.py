from django.urls import include, path

from core import views

urlpatterns = [
    path('<str:scope>', views.Index.as_view()),
]

# If using an existing urlpatterns, the viewsets can be used instead.
#from rest_framework import routers
#router = routers.DefaultRouter()
#router.register(r'state', views.StateViewSet)
#urlpatterns += [
#    path('api/', include(router.urls)),
#]
