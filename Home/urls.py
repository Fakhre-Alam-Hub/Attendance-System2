from django.urls import path
from Home import views

urlpatterns = [
    path('', views.index, name='home_index'),    
    path('about/', views.about, name='home_about'),
    path('magic/', views.magic, name='home_magic'),
    
    path('attendance_entry/', views.attendance_entry, name='home_attendance_entry'),
    path('attendance_exit/', views.attendance_exit, name='home_attendance_exit'),
    path('entry_video_feed/', views.entry_video_feed, name='home_entry_video_feed'),
    path('exit_video_feed/', views.exit_video_feed, name='home_exit_video_feed'),
    path('extract/', views.extract_features, name='home_extract_features'),
    
    path('genearte_report/', views.generate_report, name='home_genearte_report'),
    path('send_email/', views.send_email, name='home_send_email'),
    
    path('all_attendance/', views.all_attendance, name='home_all_attendance'),
    path('my_attendance/', views.my_attendance, name='home_my_attendance'),
    path('view_attendance_home/', views.view_attendance_home, name='home_view_attendance_home'),
    path('view_my_attendance_employee_login/', views.view_my_attendance_employee_login, name='home_view_my_attendance_employee_login'),

]

