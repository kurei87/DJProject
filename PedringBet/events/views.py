from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Event, Outcome
from .serializers import (
    CategorySerializer, EventSerializer, EventCreateSerializer,
    EventUpdateSerializer, OutcomeSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    pagination_class = None


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'start_time']
    search_fields = ['title', 'description']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['-start_time']

    def get_serializer_class(self):
        if self.action == 'create':
            return EventCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EventUpdateSerializer
        return EventSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        if self.action == 'list':
            return []
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_in = self.request.query_params.get('status__in')
        if status_in:
            statuses = [s.strip() for s in status_in.split(',')]
            queryset = queryset.filter(status__in=statuses)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class OutcomeViewSet(viewsets.ModelViewSet):
    queryset = Outcome.objects.all()
    serializer_class = OutcomeSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['odds']

    def get_queryset(self):
        queryset = super().get_queryset()
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset
