import os
import cv2
import numpy as np
import pandas as pd
import face_recognition
from numpy import save
from Home.models import attendanceEntry
import datetime
from django.contrib import messages
from Accounts.models import User, Profile
from django.http.response import StreamingHttpResponse
from Home.camera import VideoCamera
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Home.models import attendanceEntry, Present

from Home.utils import total_number_employees, employees_present_today, calculate_hours, save_attendance_pie_chart
from Home.forms import DateForm_2

from Home.filters import AttendanceFilter


from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage

from django_pandas.io import read_frame
import matplotlib.pyplot as plt
import seaborn as sns

def index(request):
    return render(request, 'Home/index.html')

def attendance_entry(request):
    return render(request, 'Home/attendance_entry.html')

def attendance_exit(request):
    return render(request, 'Home/attendance_exit.html')

def all_attendance(request):     
    all_attendance_qs = attendanceEntry.objects.all()
    row_count = len(all_attendance_qs)
    
    attendancefilter = AttendanceFilter(request.GET, queryset=all_attendance_qs)
    attendance_data = attendancefilter.qs
    
    hours = calculate_hours(all_attendance_qs)
    
    result = zip(attendance_data, hours)
    
    work_hour = datetime.timedelta(hours=9)
    
    context = {'result':result, 'row_count':row_count, 'attendancefilter':attendancefilter, 'work_hour':work_hour}
    return render(request,'Home/all_attendance.html',context=context)

def generate_report(request):
    
    all_attendance_qs = attendanceEntry.objects.all()
    row_count = len(all_attendance_qs)
    
    attendancefilter = AttendanceFilter(request.GET, queryset=all_attendance_qs)
    attendance_data = attendancefilter.qs
    
    hours = []
    for i in all_attendance_qs:
        if i.exit_time == None:
            hours.append(datetime.datetime.now() - i.entry_time)
        else:
            hours.append(i.exit_time - i.entry_time)
    
    result = zip(attendance_data, hours)
    context = {'result':result, 'row_count':row_count, 'attendancefilter':attendancefilter}
    print("Generating report...")
    messages.success(request, 'Report is generated!')
    
    qs = User.objects.all()
    username = []
    for i in qs:
        username.append(i.username)
        
    for i in username:
        user_qs = all_attendance_qs.filter(name=i)
        df = read_frame(user_qs)
        df.to_excel(f'media/pdfs/{i}.xlsx')
        print(f'{i}.xlsx generated')
    
    return render(request,'Home/all_attendance.html',context=context)

def send_email(request):
    qs = User.objects.all()
    
    for i in qs:    
        subject = 'Attendance Report'
        message = f'Hi {i.first_name} {i.last_name}, Your attendance report is attached below.'
        
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [i.email, ]
        
        msg = EmailMessage(subject, message, email_from, recipient_list)
        msg.content_subtype = "html" 
        msg.attach_file(f'media/pdfs/{i.username}.xlsx')
        msg.send()
    
        # send_mail( subject, message, email_from, recipient_list )
    messages.success(request, 'Email send successfully!')
    
    return render(request, 'Home/all_attendance.html')

def my_attendance(request):     
    my_attendance_qs = attendanceEntry.objects.filter(name=request.user)
    row_count = len(my_attendance_qs)
    
    hours = calculate_hours(my_attendance_qs)
    
    result = zip(my_attendance_qs, hours)
    
    save_attendance_pie_chart(my_attendance_qs)
    
    work_hour = datetime.timedelta(hours=9)
    
    context = {'result':result, 'row_count':row_count, 'work_hour':work_hour}
    return render(request,'Home/my_attendance.html',context=context)

def extract_features(request):

    all_user = User.objects.all()
    all_profile = Profile.objects.all()

    known_face_names = []
    images = []
    for user in all_user:
        profile = all_profile.get(user_id=user.id)
        img_path = profile.image
        cur_img = cv2.imread(f"{'media'}/{img_path}")
        images.append(cur_img)
        known_face_names.append(user.username)

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    known_face_encodings = findEncodings(images)
    # save image encodings to npy file
    # default_storage.save(known_face_encodings.npy, known_face_encodings)
    save("media/known_face_encodings.npy", known_face_encodings)
    # save name to npy file
    # default_storage.save(known_face_names.npy, known_face_names)
    save("media/known_face_names.npy", known_face_names)
    messages.success(request, 'Feature extraction has been done!')

    data = attendanceEntry.objects.all()
    context = {
        'all_data': data,
    }

    return render(request, 'Home/index.html', context)



def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def entry_video_feed(request):
    vid = StreamingHttpResponse(gen(VideoCamera(mode='Entry')), content_type='multipart/x-mixed-replace charset=utf-8; boundary=frame')
    return vid

def exit_video_feed(request):
    vid = StreamingHttpResponse(gen(VideoCamera(mode='Exit')), content_type='multipart/x-mixed-replace charset=utf-8; boundary=frame')
    return vid



def view_attendance_home(request):
    total_num_of_emp = total_number_employees()
    emp_present_today = employees_present_today()
    
    today = datetime.date.today()
    my_attendance_qs = attendanceEntry.objects.filter(entry_date=today)
    row_count = len(my_attendance_qs)
    
    usernames = []
    for i in my_attendance_qs:
        usernames.append(i.name)
        
    userdata = User.objects.filter(username__in = usernames)
    
    first_name, last_name = [], []
    for i in userdata:
        first_name.append(i.first_name)
        last_name.append(i.last_name)
    
    my_attendance_data = zip(my_attendance_qs, first_name, last_name)
    
    context = {'my_attendance_data':my_attendance_data, 'row_count':row_count, 'total_num_of_emp':total_num_of_emp, 'emp_present_today':emp_present_today}
    return render(request, 'Home/view_attendance_home.html', context)


@login_required
def view_my_attendance_employee_login(request):
    qs = None
    attendance_qs = None
    present_qs = None
    
    if request.method == 'POST':
        form = DateForm_2(request.POST)
        if form.is_valid():
            u = request.user
            print('user', u)
            attendance_qs = attendanceEntry.objects.filter(name = u)
            present_qs = Present.objects.filter(user_id = 2)
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            if date_to < date_from:
                messages.warning(request, f'Invalid date selection.')
                return redirect('home_view_my_attendance_employee_login')
			
            
            else:
                attendance_qs = attendance_qs.filter(entry_date__gte=date_from).filter(entry_date__lte=date_to)
                present_qs = present_qs.filter(date__gte=date_from).filter(date__lte=date_to)
            
                if (len(attendance_qs)>0 or len(present_qs)>0):
                    qs = hours_vs_date_given_employee(present_qs, attendance_qs, admin=False)
                    return render(request,'Home/view_my_attendance_employee_login.html', {'form' : form, 'qs' :qs})
                else:                    
                    messages.warning(request, f'No records for selected duration.')
                    return redirect('home_view_my_attendance_employee_login')
    else:
        form = DateForm_2()
        return render(request,'Home/view_my_attendance_employee_login.html', {'form' : form, 'qs' :qs})
	
                
              
def about(request):
    return render(request, 'Home/about.html')


def magic(request):
    return render(request, 'Home/magic.html')

