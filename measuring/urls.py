from django.urls import path
from .views import TrafficCountAPIView

urlpatterns = [
    path('api/traffic/', TrafficCountAPIView.as_view(), name='traffic-api'),
]
