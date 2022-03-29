import datetime
from django.contrib.auth.models import User
from Home.models import attendanceEntry, Present

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from django_pandas.io import read_frame
from pandas.plotting import register_matplotlib_converters
from matplotlib import rcParams
import math

from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage

def update_attendance_in_db_entry(name):
    today = datetime.date.today()
    time = datetime.datetime.now()
    
    status = attendanceEntry.objects.filter(name=name, entry_date=today).exists()
    if not status:
        entry = attendanceEntry(name=name, entry_date=today, entry_time=time)
        entry.save()
        
        user = User.objects.get(username=name)
        print('user: ', user)
        try:
            qs = Present.objects.get(user=user,date=today)
        except :
            qs = None
        if qs is None:
            a = Present(user=user,date=today,present=True)
            a.save()
        else:
            qs.present=True
            qs.save(update_fields=['present'])

def update_attendance_in_db_exit(name):
    today = datetime.date.today()
    time = datetime.datetime.now()
    
    status = attendanceEntry.objects.filter(name=name, exit_date=today).exists()
    if not status:
        qs = attendanceEntry.objects.filter(name=name, entry_date=today).exists()
        if qs:
            qs = attendanceEntry.objects.get(name=name, entry_date=today)
            qs.exit_time = time
            qs.exit_date = today
            qs.save(update_fields=['exit_time','exit_date'])
            
        working_hours = datetime.timedelta(hours=9)
        user_qs = attendanceEntry.objects.filter(name=name, entry_date=today)
        for i in user_qs:
            if i.exit_time is not None and i.entry_time is not None:
                if i.exit_time - i.entry_time < working_hours:
                    user = User.objects.get(username=name)
                    subject = "Attendance Alert"
                    message = "Dear {0} {1}, Today you exited early.\nRequired working hour is 9.\nYour working hour for {2} is {3}.\n\nRegards,\n\nAugust Infotech Recognition".format(user.first_name, user.last_name, today, i.exit_time - i.entry_time)
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [user.email]
                    msg = EmailMessage(subject, message, email_from, recipient_list)
                    # msg.content_subtype = "html"
                    msg.send()
                    print("working hours: less than 9", i.exit_time - i.entry_time)

def total_number_employees():
	qs = User.objects.all()
	return len(qs)

def employees_present_today():
	today = datetime.date.today()
	qs = Present.objects.filter(date = today).filter(present = True)
	return len(qs)

def view_attendance_home(request):
	total_num_of_emp = total_number_employees()
	emp_present_today = employees_present_today()

def calculate_hours(qs):
    hours = []
    for i in qs:
        if i.exit_time == None:
            hours.append(datetime.datetime.now() - i.entry_time)
        else:
            hours.append(i.exit_time - i.entry_time)
    return hours

def save_attendance_pie_chart(qs):
    date1 = datetime.date(2022,3,1)
    today = datetime.date.today()
    total_days = np.busday_count(np.datetime64(date1), np.datetime64(today), weekmask='1111100') + 1
    
    daterange = []
    for i in qs:
        daterange.append(i.entry_time)

    date_strt, date_end = pd.to_datetime(date1), pd.to_datetime(today)
    present_count = 0
    for ele in daterange:
        if (ele >= date_strt) and (ele <= date_end + datetime.timedelta(days=1)) and (ele.weekday() < 5):
            present_count += 1
    
    
    def func(pct, allvalues):
        absolute = int(pct / 100.*np.sum(allvalues))
        return "{:.2f}%\n({:d} days)".format(pct, absolute)

    data = [present_count, total_days-present_count]
    labels = ['Present', 'Absent']
    colors = sns.color_palette('bright')[0:5]
    plt.pie(data, labels = labels, colors = colors, autopct=lambda pct: func(pct, data), explode=[0,0.1])
    # plt.title('Attendance Pie Chart')
    plt.legend(labels, loc='best')
    plt.savefig('./Home/static/Home/img/attendance_graphs/employee_attendance_percent/1.png')
    plt.close()