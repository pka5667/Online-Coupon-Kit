from django.db import models
from django.urls import reverse



# ALL CATEGORIES MODEL
class Category(models.Model):
    category    = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.category
    


# UDEMY COURSE MODEL
class Udemy_Course(models.Model):
    model_title         = models.CharField(max_length=100, unique=True)
    title               = models.CharField(max_length=100)
    description         = models.CharField(max_length=100)
    category            = models.ManyToManyField('Category')
    thumbnail           = models.URLField()
    what_you_will_learn = models.CharField(max_length=1000)
    original_price      = models.CharField(max_length=50)
    coupon_code         = models.CharField(max_length=50)
    course_url          = models.URLField(max_length=50, unique=True)
    last_updated        = models.DateTimeField(auto_now=True, auto_now_add=False)


    def get_category(self):
        return [str(category) for category in self.category.all()]
    
    def get_absolute_url(self):
        return reverse("course_detail", args=[self.model_title,])
    
