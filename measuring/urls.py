from django.urls import path
from .views import TrafficCountAPIView

urlpatterns = [
    path('traffic/', TrafficCountAPIView.as_view(), name='traffic-api'),
]
