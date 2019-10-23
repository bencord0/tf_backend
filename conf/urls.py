from django.urls import include, path

from core import views

urlpatterns = [
    path('<str:pk>', views.Index.as_view()),
]
