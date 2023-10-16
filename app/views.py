from .forms import *
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.db.models import Case, When, Value, IntegerField
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
#registrasi

def is_dosen(user):
    return user.role == 'Dosen'
def is_mahasiswa(user):
    return user.role == 'Mahasiswa'
def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
@login_required
def registration_view(request):
    if not is_admin(request.user):
        # If the user is not an admin, display a JavaScript alert
        alert_script = "<script>alert('You are not an admin. Access denied.')</script>"
        return HttpResponse(alert_script)

    if request.method == 'POST':
        form = RegistrationForm(request.POST,request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # hash password
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
# login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                if user.role == 'Mahasiswa':
                    return redirect('mhs')
                elif user.role == 'Dosen':
                    return redirect('dsn_dashboard')
                elif user.is_staff:
                    return redirect('admin:index')
            else:
                error_message = "Invalid credentials. Please try again."
                return render(request, 'registration/login.html', {'form': form, 'error_message': error_message})
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@user_passes_test(is_dosen)
def dsn(request):
    current_user = request.user
    hari_ini = timezone.now().strftime("%A").upper()

    hari_order = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
    jadwal = JadwalMengajar.objects.filter(dosen=current_user).order_by(
        Case(
            *[When(hari=h, then=Value(pos)) for pos, h in enumerate(hari_order)],
            default=Value(len(hari_order)),
            output_field=IntegerField()
        )
    )

    if 'hari' in request.GET:
        hari_ini = request.GET['hari'].upper()
        jadwal = jadwal.filter(hari=hari_ini)

    context = {
        'jadwal': jadwal,
        'hari_ini': hari_ini,
    }

    return render(request, 'dosen/dashboard.html', context)

#tugas
@user_passes_test(is_dosen)
def create_assignment(request):
    if request.user.role == 'Dosen':
        if request.method == 'POST':
            form = AssignmentForm(request.POST, request.FILES)
            if form.is_valid():
                assignment = form.save(commit=False)
                assignment.author = request.user
                assignment.save()
                return redirect('dsn_dashboard')
        else:
            form = AssignmentForm()
        return render(request, 'tugas/create_assignment.html', {'form': form})
    else:
        return redirect('student_dashboard')

@user_passes_test(is_dosen)
def view_assignment(request):
    assignments = Assignment.objects.filter(author=request.user)

    # Ambil nilai date_filter dari request.GET
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_query = request.GET.get('search_query')

    # Ambil nilai start_date dan end_date dari request.GET
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        # Gunakan Q objects untuk mencari range tanggal
        assignments = Assignment.objects.filter(Q(author=request.user), Q(deadline__date__gte=start_date), Q(deadline__date__lte=end_date))
    else:
        assignments = Assignment.objects.filter(author=request.user)

    if search_query:
        # Gunakan Q objects untuk mencari judul yang mengandung search_query
        assignments = assignments.filter(Q(title__icontains=search_query))

    # Urutkan assignments berdasarkan tanggal pembuatan (atau tanggal unggah jika ingin)
    # assignments = assignments.order_by('-id')  # Ubah sesuai dengan atribut yang ingin diurutkan
    assignments = assignments.order_by('-id')

    # Paginasi dengan 5 items per halaman
    paginator = Paginator(assignments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dosen/view_ass.html', {'page_obj': page_obj})

def view_grade(request):
    form = DateFilterForm(request.GET)
    user_submissions = Submission.objects.filter(author=request.user)
    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        
        if start_date:
            user_submissions = user_submissions.filter(submission_time__gte=start_date)
        if end_date:
            user_submissions = user_submissions.filter(submission_time__lte=end_date)
    
    grades = AssignmentGrade.objects.filter(submission__in=user_submissions)
    
    return render(request, 'mahasiswa/lihat_nilai.html', {'grades': grades, 'form': form})

# @login_required
def view_assigned_assignments(request):
    form = AssignmentFilterForm(request.GET)
    assigned_assignments = Assignment.objects.filter(author=request.user)
    graded_assignments = []
    ungraded_assignments = []

    # Ambil status dari form
    status = form.data.get('status')

    for assignment in assigned_assignments:
        submissions = Submission.objects.filter(assignment=assignment)
        graded_submissions = AssignmentGrade.objects.filter(submission__in=submissions)

        if status == 'graded' and graded_submissions:
            graded_assignments.append({
                'assignment': assignment,
                'status': 'Sudah Dinilai',
                'graded_submissions': graded_submissions
            })
        elif status == 'ungraded' and not graded_submissions:
            ungraded_assignments.append({
                'assignment': assignment,
                'status': 'Belum Dinilai'
            })
        elif status == 'all':
            if graded_submissions:
                graded_assignments.append({
                    'assignment': assignment,
                    'status': 'Sudah Dinilai',
                    'graded_submissions': graded_submissions
                })
            else:
                ungraded_assignments.append({
                    'assignment': assignment,
                    'status': 'Belum Dinilai'
                })

    return render(request, 'dosen/view_assigned_assignments.html', {'graded_assignments': graded_assignments, 'ungraded_assignments': ungraded_assignments, 'form': form})

# @login_required
def view_grade_dsn(request, submission_id):
    # Ambil tugas berdasarkan ID
    assignment = get_object_or_404(Assignment, id=submission_id)

    # Ambil semua submission terkait dengan tugas ini
    submissions = Submission.objects.filter(assignment=assignment)

    # Inisialisasi sebuah dictionary untuk menyimpan nilai dan pengirim tugas
    grades_data = {}

    for submission in submissions:
        try:
            # Ambil nilai untuk submission ini
            grade = AssignmentGrade.objects.get(submission=submission)
            grades_data[submission] = grade
        except AssignmentGrade.DoesNotExist:
            grades_data[submission] = None

    return render(request, 'dosen/view_grade.html', {'assignment': assignment, 'grades_data': grades_data})


def edit_dsn_profile(request):
    Dsn = CustomUser.objects.get(id=request.user.id)

    if request.method == 'POST':
        form = StudentProfileAndPasswordForm(request.POST, request.FILES, instance=Dsn)  # Menambahkan request.FILES untuk menangani berkas
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            if new_password:
                Dsn.set_password(new_password)
                update_session_auth_hash(request, Dsn)

            # Periksa apakah ada berkas gambar yang diunggah
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                Dsn.image.save(image_file.name, image_file)  # Simpan berkas gambar ke model

            form.save()
            messages.success(request, 'Your profile and password were successfully updated!')
            return redirect('mhs')
    else:
        form = StudentProfileAndPasswordForm(instance=Dsn)


    return render(request, 'dosen/edit_profile.html', {'form': form})

@user_passes_test(is_dosen)
def view_submissions(request, assignment_id):
    # Pastikan hanya Dosen yang dapat mengakses halaman ini
    if request.user.role != 'Dosen':
        return redirect('student_dashboard')

    try:
        # Cari tugas berdasarkan ID yang diberikan
        assignment = Assignment.objects.get(id=assignment_id, author=request.user)

        # Ambil semua pengiriman tugas untuk tugas ini
        submissions = Submission.objects.filter(assignment=assignment)

        return render(request, 'dosen/view_submissions.html', {'assignment': assignment, 'submissions': submissions})
    except Assignment.DoesNotExist:
        # Jika tugas tidak ditemukan, lakukan sesuatu (misalnya, tampilkan pesan kesalahan atau redirect)
        return redirect('dsn_dashboard')
        
@user_passes_test(is_dosen)
def grade_assignment(request, submission_id):
    # Pastikan hanya Dosen yang dapat mengakses halaman ini
    if request.user.role != 'Dosen':
        return redirect('student_dashboard')

    submission = get_object_or_404(Submission, id=submission_id)
    assignment = submission.assignment

    # Cek apakah sudah ada nilai untuk pengiriman ini
    assignment_grade, created = AssignmentGrade.objects.get_or_create(submission=submission, grader=request.user)

    if request.method == 'POST':
        form = AssignmentGradeForm(request.POST, instance=assignment_grade)
        if form.is_valid():
            # Pastikan nilai grade telah diatur
            if 'grade' in form.cleaned_data:
                assignment_grade.grade = form.cleaned_data['grade']
            assignment_grade.save()  # Simpan objek AssignmentGrade setelah mengatur nilai grade
            return redirect('view_ass')
    else:
        form = AssignmentGradeForm(instance=assignment_grade)

    return render(request, 'dosen/grade_assignment.html', {'form': form, 'submission': submission, 'assignment': assignment})
    
def mhs(request):
    # Dapatkan pengguna saat ini
    current_user = request.user

    # Pastikan pengguna memiliki role Mahasiswa
    if current_user.role != CustomUser.Mahasiswa:
        return render(request, 'jadwal_mhs.html', {'error_message': 'Anda tidak memiliki izin untuk mengakses halaman ini.'})

    # Dapatkan hari saat ini
    current_day = timezone.now().strftime("%A").upper()

    # Dapatkan jadwal berdasarkan semester dan jurusan
    jadwal = JadwalMengajar.objects.filter(semester=current_user.semester, jurusan=current_user.department)

    # Jika terdapat filter berdasarkan hari
    if 'hari' in request.GET:
        current_day = request.GET['hari'].upper()
        if current_day == 'HARI_INI':
            current_day = timezone.now().strftime("%A").upper()
        elif current_day == 'SEMUA':
            pass  # Tidak perlu menyaring berdasarkan hari
        else:
            jadwal = jadwal.filter(hari=current_day)

    context = {
        'jadwal': jadwal,
        'current_day': current_day,
    }

    return render(request, 'jadwal_mhs.html', context)

def profileMHS(request):
    return render(request, 'mahasiswa/profile.html')

def profileDSN(request):
    return render(request, 'dosen/profile.html')
def edit_student_profile(request):
    author = CustomUser.objects.get(id=request.user.id)

    if request.method == 'POST':
        form = StudentProfileAndPasswordForm(request.POST, request.FILES, instance=author)  # Menambahkan request.FILES untuk menangani berkas
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            if new_password:
                author.set_password(new_password)
                update_session_auth_hash(request, author)

            # Periksa apakah ada berkas gambar yang diunggah
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                author.image.save(image_file.name, image_file)  # Simpan berkas gambar ke model

            form.save()
            messages.success(request, 'Your profile and password were successfully updated!')
            return redirect('mhs')
    else:
        form = StudentProfileAndPasswordForm(instance=author)

    return render(request, 'mahasiswa/edit_profile.html', {'form': form})


def list_tugas_mhs(request):
    user = request.user

    if 'q' in request.GET:
        query = request.GET['q']
        assignments = Assignment.objects.filter(semester=user.semester, departement=user.department, title__icontains=query).order_by('deadline')
    else:
        assignments = Assignment.objects.filter(semester=user.semester, departement=user.department).order_by('deadline')

    # Tambahkan paginasi di sini
    paginator = Paginator(assignments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'mahasiswa/list_tgs.html', {'page_obj': page_obj})



def detail_tgs_mhs(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    print(assignment)
    return render(request, 'mahasiswa/detail_tgs.html', {'assignment': assignment})


def daftar_tugas(request):
    tanggal = request.GET.get('tanggal')
    filter_option = request.GET.get('filter')
    semester = request.user.semester
    jurusan = request.user.department

    assignments = Assignment.objects.filter(semester=semester, departement=jurusan).order_by('deadline')
    submission_count = 0  

    if tanggal:
        try:
            tanggal = datetime.strptime(tanggal, "%Y-%m-%d").date()
            assignments = assignments.filter(deadline__date=tanggal)
        except ValueError:
            pass

    if filter_option == 'deadline':
        assignments = assignments.order_by('deadline')
    elif filter_option == 'sudah_terkirim':
        submission_count = Submission.objects.filter(author=request.user, assignment__in=assignments).count()
        assignments = assignments.filter(submission__author=request.user)
    elif filter_option == 'belum_dikerjakan':
        submission_count = assignments.exclude(submission__author=request.user).count()
        assignments = assignments.exclude(submission__author=request.user)

    paginator = Paginator(assignments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'mahasiswa/daftar_tugas.html', {
        'assignments': assignments,
        'filter_option': filter_option,
        'submission_count': submission_count, 
        'page_obj': page_obj,
    })

def upload_tugas(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    existing_submission = Submission.objects.filter(author=request.user, assignment=assignment).first()

    deadline = assignment.deadline

    deadline = assignment.deadline

    current_time = timezone.now()

    is_submission_open = current_time <= deadline

    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            if is_submission_open:
                submission = form.save(commit=False)
                submission.author = request.user
                submission.assignment = assignment

                if existing_submission:
                    existing_submission.attachment = submission.attachment
                    existing_submission.save()
                else:
                    submission.save()

                return redirect('daftar_tugas')
            else:
                return redirect('daftar_tugas')
    else:
        form = AssignmentSubmissionForm()

    return render(request, 'mahasiswa/upload_tugas.html', {
        'form': form,
        'assignment': assignment,
        'existing_submission': existing_submission,
        'is_submission_open': is_submission_open,
    })
def edit_submission(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submission = get_object_or_404(Submission, author=request.user, assignment=assignment)
    deadline = assignment.deadline
    current_time = timezone.now()
    is_submission_open = current_time <= deadline

    if not is_submission_open:
        return redirect('daftar_tugas')

    if request.method == 'POST':
        form = EditSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            return redirect('daftar_tugas')
    else:
        form = EditSubmissionForm(instance=submission)

    return render(request, 'mahasiswa/edit_kiriman.html', {
        'form': form,
        'assignment': assignment,
    })

def logout_view(request):
    logout(request)
    return redirect('login')
