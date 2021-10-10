from django.contrib import admin
from .models import Category, Udemy_Course

# Register your models here.
admin.site.register(Category)

@admin.register(Udemy_Course)
class Udemy_Course_Admin(admin.ModelAdmin):
    list_display = ['id', 'title', 'original_price', 'get_category', 'course_url', 'last_updated']

