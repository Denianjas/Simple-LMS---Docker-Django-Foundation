from celery import shared_task
import time
import csv
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import Course, Enrollment

User = get_user_model()

@shared_task
def send_enrollment_email(student_id, course_title):
    try:
        student = User.objects.get(id=student_id)
        subject = f"Selamat! Kamu Berhasil Terdaftar di {course_title}"
        message = f"Halo {student.username},\n\nKamu telah sukses terdaftar di kelas {course_title}. Selamat belajar!"
        
        send_mail(subject, message, 'admin@lms.com', [student.email], fail_silently=False)
        return f"Email pendaftaran berhasil dikirim ke {student.email}"
    except User.DoesNotExist:
        return "User tidak ditemukan"

@shared_task
def generate_certificate(student_username, course_title):
    time.sleep(5) 
    return f"Sertifikat_{student_username}_{course_title}.pdf"

@shared_task
def update_course_statistics():
    courses = Course.objects.all()
    for course in courses:
        total_students = Enrollment.objects.filter(course=course).count()
        print(f"Course: {course.title} | Total Siswa Aktif: {total_students}")
    return "Statistik berhasil diperbarui."

@shared_task
def export_course_report(filename="laporan_course.csv"):
    time.sleep(3) 
    courses = Course.objects.all()
    with open(f"/app/{filename}", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID Course", "Judul Kelas", "Instruktur"])
        for course in courses:
            writer.writerow([course.id, course.title, course.instructor.username])
            
    return f"File {filename} siap diunduh."