from django.urls import path
from .views import intranet_dashboard, ActivityListView, ActivityCreateView, ActivityUpdateView, ActivityDeleteView

urlpatterns = [
    path('intranet/', intranet_dashboard, name='intranet_dashboard'),
    path('sitio/', ActivityListView.as_view(), name='hugo_activity_list'),
    path('sitio/add/', ActivityCreateView.as_view(), name='hugo_activity_create'),
    path('sitio/<int:pk>/edit/', ActivityUpdateView.as_view(), name='hugo_activity_update'),
    path('sitio/<int:pk>/delete/', ActivityDeleteView.as_view(), name='hugo_activity_delete'),
]
