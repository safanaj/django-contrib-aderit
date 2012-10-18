from django import forms
from django.contrib import admin
from django.db import models
from django.contrib.aderit.news.models import NewsItem


class NewsItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}
    list_display = ['title', 'pub_date']
    list_filter = ['pub_date']
    search_fields = ['title', 'body']
    date_hierarchy = 'pub_date'
    ordering = ['-pub_date']
    fieldsets = (
        ('Article info', {
                'fields': ('title', 'body', 'pub_date',)
                }),
        ('Advanced', {
                'classes': ['collapse'],
                'fields': ('snippet', 'slug',)
                }),
        )

admin.site.register(NewsItem, NewsItemAdmin)
