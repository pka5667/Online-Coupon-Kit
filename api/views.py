from django.utils.decorators import method_decorator
from core.models import Udemy_Course
from .serializers import UdemyCourseSerializer
from rest_framework import viewsets
from rest_framework.views import Response
from django.views.decorators.cache import cache_page


# VIEW FUNCTION
class UdemyCourseReadOnlyViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(60*60*24))
    def list(self, request):
        courses = Udemy_Course.objects.all().order_by('-last_updated')[:20]
        serializer = UdemyCourseSerializer(courses, many=True)
        return Response(serializer.data)

    @method_decorator(cache_page(60*60*24))
    def retrieve(self, request, pk):
        courses = Udemy_Course.objects.filter(model_title__icontains=pk).order_by('-last_updated')[:10]
        serializer = UdemyCourseSerializer(courses, many=True)
        return Response(serializer.data)
