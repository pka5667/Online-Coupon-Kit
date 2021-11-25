from django.contrib.sitemaps import Sitemap
from .models import Udemy_Course
from django.core.cache import cache


class UdemyCourseSitemap(Sitemap):
    def items(self):
        if not cache.get("sitemap_udemy_courses"):
            cache.set("sitemap_udemy_courses", Udemy_Course.objects.all().order_by('-last_updated'), timeout=500000)
        return cache.get("sitemap_udemy_courses")

