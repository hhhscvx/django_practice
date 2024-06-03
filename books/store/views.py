from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Book
from .serializers import BookSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated] # Авторизация - можно ли опред. юзеру делать что-либо
    filterset_fields = ['price']
    search_fields = ['title', 'author']
    ordering_fields = ['price', 'author']


def auth(request):
    return render(request, 'oauth.html')
