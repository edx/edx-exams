from django.urls import path

from . import views

app_name = 'lti'
urlpatterns = [
    path('start_proctoring', views.start_proctoring),
    path('authenticate', views.authenticate),
    path('start_assessment', views.start_assessment, name='start-assessment'),
    path('end_assessment', views.end_assessment),
    path('public_keyset', views.public_keyset),
]
