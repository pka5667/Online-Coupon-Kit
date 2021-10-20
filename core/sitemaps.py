from django.contrib.sitemaps import Sitemap
from .models import Udemy_Course


class UdemyCourseSitemap(Sitemap):
    def items(self):
        return Udemy_Course.objects.all().order_by('-last_updated')

