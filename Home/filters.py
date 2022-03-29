import django_filters
from django_filters import DateFilter, CharFilter, NumberFilter
from .models import *
        
        
class AttendanceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='User ID contains')
    
    # release_year = django_filters.NumberFilter(field_name='release_date', lookup_expr='year')
    # release_year__gt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__gt')
    # release_year__lt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__lt')
    
    # total_experience_gte = django_filters.NumberFilter(field_name='total_experience', lookup_expr='gte')
    # total_experience_lte = django_filters.NumberFilter(field_name='total_experience', lookup_expr='lte')
    
    # skills = django_filters.CharFilter(field_name='skills', lookup_expr='icontains')
    # degree = django_filters.CharFilter(field_name='degree', lookup_expr='icontains')

    class Meta:
        model = attendanceEntry
        fields = ['name']
