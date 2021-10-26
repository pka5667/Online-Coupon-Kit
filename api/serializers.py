from django.urls import reverse
from core.models import Udemy_Course
from rest_framework import serializers

class UdemyCourseSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return 'https://www.onlinecouponkit.tk'+reverse('redirect_to_course', kwargs={'model_title': obj.model_title})
    
    class Meta:
        model = Udemy_Course
        fields = ['url', 'title', 'description', 'category', 'thumbnail', 'what_you_will_learn', 'original_price', 'coupon_code', 'last_updated']

