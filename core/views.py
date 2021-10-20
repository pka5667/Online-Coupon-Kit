from django.http.response import HttpResponseForbidden
from django.shortcuts import render, HttpResponse
from .models import Udemy_Course, Category
from django.core.paginator import Paginator
import random
import re # for scrapper view model title name
import os # for env
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.cache import cache_page



# HOME PAGE VIEW
# CHECK FOR CATEGORY AND SEARCH REQUEST BOTH 
@cache_page(60*60*24)
def index(request, category=None, search=None):
    # cache sql queries for 12 hrs according to category
    if category == None:
        all_courses     = Udemy_Course.objects.all().order_by('-last_updated')
    else:
        all_courses     = Udemy_Course.objects.filter(category = Category.objects.get(category=category)).order_by('-last_updated')
    all_categories      = Category.objects.all().order_by('category')

    # check search query 
    if search:
        regex               = re.compile('[^a-zA-Z0-9]')
        search              = regex.sub(' ', search)
        q = None
        for word in search.split(' '):
            if q: q = q & (Q(title__icontains= word) | Q(what_you_will_learn__icontains= word))
            else: q = Q(title__icontains= word) | Q(what_you_will_learn__icontains= word)
        all_courses = all_courses.filter(q).order_by('-last_updated')
    
    # check page number query
    paginator           = Paginator(all_courses, 16, 4)
    page_number         = request.GET.get('page', 1) #default 1
    page_obj            = paginator.get_page(page_number)
    return render(request, 'core/home.html', {'page_obj': page_obj, 'curr_category': category, 'categories': all_categories})


# COURSE DETAIL VIEW 
@cache_page(60*60*24)
def CourseView(request, model_title):
    course                      = Udemy_Course.objects.get(model_title=str(model_title))
    course.what_you_will_learn  = str(course.what_you_will_learn).replace('\n', '<br>').replace('\\n', '<br>')
    recommended                 = Udemy_Course.objects.all().order_by('-last_updated')[:50]
    recommended                 = list(recommended)
    random.shuffle(recommended)
    recommended = recommended[:12]
    return render(request, 'core/course_detail.html', {'course': course, 'recommended': recommended})


# redirect view 
def redirect_to_course(request, model_title):
    course = Udemy_Course.objects.get(model_title=model_title)
    return render(request, 'core/redirect_to_course.html', {'course': course})


# about view 
def about(request):
    return render(request, 'core/about.html')


# contact view 
def contact(request):
    return render(request, 'core/contact.html')



# Add Course View
@csrf_exempt
def AddCourseView(request):
    if request.method == 'GET' or os.environ.get('DATABASE_ACCESS_PASSWORD') != request.POST.get('password', default=''):
        return HttpResponseForbidden()
    
    # now add course to model 
    try:
        regex = re.compile('[^a-zA-Z0-9]')
        #regex - First parameter is the replacement, second parameter is your input string
        new_title           = regex.sub('-', request.POST.get('title')).replace('--', ' ').replace(' -', ' ').replace('- ', ' ').replace('  ', ' ')
        new_model_title     = regex.sub('-', new_title)

        # if udemy course with url is already present
        course_with_same_url    = Udemy_Course.objects.filter(course_url=request.POST.get('course_url'))
        course_obj              = Udemy_Course( model_title = new_model_title, 
                                                title = request.POST.get('title'), 
                                                description = request.POST.get('description'), 
                                                thumbnail = request.POST.get('thumbnail_url'), 
                                                what_you_will_learn = request.POST.get('what_you_will_learn'), 
                                                original_price = request.POST.get('original_price'), 
                                                coupon_code = request.POST.get('coupon_code'), 
                                                course_url = request.POST.get('course_url')
                                                )
        if course_with_same_url.count() != 0:
            if request.POST.get('coupon_code') == course_with_same_url[0].coupon_code:  # if there are no changes
                return HttpResponse(json.dumps({'type': 'no_change'}), content_type="application/json")
            else:
                course_obj.id = course_with_same_url[0].id
            
        # saving course and setting the Category
        course_obj.save()
        course_obj.category.add(Category.objects.get_or_create(category = request.POST.get('category'))[0])

        response_data = {
            'type': 'course added successfully',
            'title': request.POST.get('title'),
            'thumbnail_url': request.POST.get('thumbnail_url'),
            'description': request.POST.get('description'), 
            'original_price': request.POST.get('original_price'), 
            'coupon_code': request.POST.get('coupon_code'), 
            'final_course_url': f'https://www.onlinecouponkit.tk/course/{new_model_title}/'
        }

    except Exception as e:
        response_data = {
            'type': 'error',
            'error': e
        }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

