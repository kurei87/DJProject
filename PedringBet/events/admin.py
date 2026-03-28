from django.contrib import admin
from .models import Category, Event, Outcome


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


class OutcomeInline(admin.TabularInline):
    model = Outcome
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'start_time', 'end_time', 'created_by', 'created_at']
    list_filter = ['status', 'category', 'start_time']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    inlines = [OutcomeInline]


@admin.register(Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'odds', 'is_winner']
    list_filter = ['is_winner', 'event__category']
    search_fields = ['name', 'event__title']
