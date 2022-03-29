from django.db import models
import datetime
from django.contrib.auth.models import User


# Create your models here.
class attendanceEntry(models.Model):
    name = models.CharField(max_length=100, unique_for_date='entry_date')
    # name = models.ForeignKey(User, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)
    entry_date = models.DateField( auto_now_add=False, auto_now=False, blank=True, null=True)
    
    exit_time = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)
    exit_date = models.DateField( auto_now_add=False, auto_now=False, blank=True, null=True)
    


class Present(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	date = models.DateField(default=datetime.date.today)
	present = models.BooleanField(default=False)
	
# class Time(models.Model):
# 	user = models.ForeignKey(User,on_delete=models.CASCADE)
# 	date = models.DateField(default=datetime.date.today)
# 	time = models.DateTimeField(null=True,blank=True)
# 	out = models.BooleanField(default=False)