from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    path('category/<str:category>/', views.index, name="category"),
    path('search/<str:search>/', views.index, name="search"),
    path('course/<str:model_title>/', views.CourseView, name="course_detail"),
    path('course-redirect/<str:model_title>/', views.redirect_to_course, name="redirect_to_course"),
    path('add_new_course/', views.AddCourseView, name="add_new_course")
]
