from core.models import Udemy_Course
from .serializers import UdemyCourseSerializer
from rest_framework import viewsets



# VIEW FUNCTION
class UdemyCourseReadOnlyViewSet(viewsets.ModelViewSet):
    queryset = Udemy_Course.objects.all().order_by('-last_updated')[:10]
    serializer_class = UdemyCourseSerializer
