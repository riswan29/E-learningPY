from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.registration_view, name='registration'),
    path('', views.login_view, name='login'),
    path('dsn/', views.dsn, name='dsn_dashboard'),
    path('tugas/', views.create_assignment, name='create'),
    path('list_tugas/', views.view_assignment, name='view_ass'),
    path('nilai/', views.view_grade, name='view_grade'),
    path('dosen/nilai/', views.view_assigned_assignments, name='view_assigned_assignments'),
    path('view_grade/<int:submission_id>/', views.view_grade_dsn, name='view_grade_dsn'),
    path('pengirim/<int:assignment_id>/', views.view_submissions, name='pengirim'),
    path('edit_dsn/', views.edit_dsn_profile, name='edit_dsn'),
    path('grade_assignment/<int:submission_id>/', views.grade_assignment, name='grade_assignment'),
 
    path('mhs/', views.mhs, name="mhs"),
    path('mhs/profile/', views.profileMHS, name="mhs_profile"),
    path('dsn/profile/', views.profileDSN, name="dsn_profile"),
    path('daftar_tugas/', views.daftar_tugas, name='daftar_tugas'),
    path('upload_tugas/<int:assignment_id>/', views.upload_tugas, name='upload_tugas'),
    path('edit_mhs/', views.edit_student_profile, name='edit_mhs'),
    path('list_tgs/', views.list_tugas_mhs, name='list_tgs'),
    path('detail_tgs_mhs/<int:assignment_id>/',views.detail_tgs_mhs, name='detail_task'),
    path('edit_submission/<int:assignment_id>/', views.edit_submission, name='edit_kiriman'),
    path('logout/', views.logout_view, name='logout'),

]+ static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
