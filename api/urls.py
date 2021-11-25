from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('udmey_course', views.UdemyCourseReadOnlyViewSet, basename="udmey_course_api")
router.register('udemy_course', views.UdemyCourseReadOnlyViewSet, basename="udemy_course_api")


urlpatterns = [
    path('', include(router.urls)),
]

