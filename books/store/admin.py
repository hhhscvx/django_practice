from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_filter = ['price', 'title']
    search_fields = ['title']
    list_display = ['title', 'price']
