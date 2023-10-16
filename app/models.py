from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from enum import Enum

# model user
class CustomUser(AbstractUser):
    Admin = 'Admin'
    Mahasiswa = 'Mahasiswa'
    Dosen = 'Dosen'

    ROLE_CHOICES = [
        (Mahasiswa, 'Mahasiswa'),
        (Dosen, 'Dosen'),
        (Admin, 'Admin'),
    ]

    DEPARTMENT_CHOICES = (
        ('IT', 'Information Technology'),
        ('CS', 'Computer Science'),
    )

    SEMESTER_CHOICES = (
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
        ('7', 'Semester 7'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True, default=Mahasiswa)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    nidn = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, blank=True)
    semester = models.CharField(max_length=100, choices=SEMESTER_CHOICES, blank=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField(upload_to='img_profile/')


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# save file upload
def upload_to(instance, filename):
    return f'assignments/{instance.author.username}/{filename}'
#validasi file upload
def validate_file_extension(value):
    allowed_extensions = ['.pdf', '.docx', '.zip']
    if not any(value.name.endswith(ext) for ext in allowed_extensions):
        raise ValidationError('Only PDF, DOCX, and ZIP files are allowed.')
# model upload tugas
class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    semester = models.CharField(max_length=100, choices=CustomUser.SEMESTER_CHOICES)
    departement = models.CharField(max_length=100, choices=CustomUser.DEPARTMENT_CHOICES)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Dosen yang membuat tugas
    attachment = models.FileField(upload_to=upload_to, blank=True, null=True, validators=[validate_file_extension])

    def __str__(self):
        return self.title

class Submission(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    submission_time = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to=upload_to, validators=[validate_file_extension])

    def __str__(self):
        return f'{self.author.email} - {self.assignment.title}'

class AssignmentGrade(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE)
    grader = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='graded_assignments')
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        null=True  # Bidang grade boleh kosong
    )
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Grade for {self.submission.author.username} - {self.submission.assignment.title}"




class JadwalMengajar(models.Model):
    dosen = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': CustomUser.Dosen}
    )
    METODE_BELAJAR = (
        ('Luring', 'Luring'),
        ('Daring', 'Daring'),
    )
    HARI = (
        ('MONDAY', 'SENIN'),
        ('TUESDAY', 'SELASA'),
        ('WEDNESDAY', 'RABU'),
        ('THURSDAY', 'KAMIS'),
        ('FRIDAY', 'JUMAT'),
        ('SATURDAY', 'SABTU'),
    )
    mata_kuliah = models.CharField(max_length=255)
    kode_mata_kuliah = models.CharField(max_length=10)
    semester = models.CharField(max_length=1, choices=CustomUser.SEMESTER_CHOICES)
    jurusan = models.CharField(max_length=100, choices=CustomUser.DEPARTMENT_CHOICES)
    hari = models.CharField(max_length=100, choices=HARI)
    jam_mulai = models.TimeField()
    jam_berakhir = models.TimeField()
    kode_ruangan = models.CharField(max_length=10)
    metode_pembelajaran = models.CharField(max_length=100, choices=METODE_BELAJAR)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.mata_kuliah} - {self.semester} - {self.hari}"
