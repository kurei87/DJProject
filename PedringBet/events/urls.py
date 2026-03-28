from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, EventViewSet, OutcomeViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'', EventViewSet)
router.register(r'outcomes', OutcomeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
