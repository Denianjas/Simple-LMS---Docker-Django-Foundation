from django.core.management.base import BaseCommand
from django.db import connection, reset_queries
from lms_app.models import User, Category, Course

class Command(BaseCommand):
    help = 'Demo N+1 problem and Query Optimization'

    def handle(self, *args, **kwargs):

        if not Course.objects.exists():
            self.stdout.write("Membuat dummy data...")
            instructor = User.objects.create_user(username='dosen_web', role='instructor', password='123')
            cat1 = Category.objects.create(name='Programming')
            
       
            for i in range(10):
                Course.objects.create(title=f'Materi Kelas {i+1}', instructor=instructor, category=cat1)
            self.stdout.write("Dummy data berhasil dibuat!\n")

  
        from django.conf import settings
        settings.DEBUG = True 

        # ==========================================
        # SKENARIO 1: N+1 PROBLEM (TIDAK OPTIMAL)
        # ==========================================
        self.stdout.write(self.style.ERROR('--- SKENARIO N+1 PROBLEM ---'))
        reset_queries() 
        
     
        courses_unoptimized = Course.objects.all()
        for course in courses_unoptimized:
           
            print(f"{course.title} | Dosen: {course.instructor.username} | Kategori: {course.category.name}")
        
        queries_n_plus_1 = len(connection.queries)
        self.stdout.write(self.style.ERROR(f'>> Total Database Query tereksekusi (N+1): {queries_n_plus_1}\n'))

        # ==========================================
        # SKENARIO 2: OPTIMIZED (MENGGUNAKAN SELECT_RELATED)
        # ==========================================
        self.stdout.write(self.style.SUCCESS('--- SKENARIO OPTIMIZED ---'))
        reset_queries() 
        
      
        courses_optimized = Course.objects.for_listing()
        for course in courses_optimized:
           
            print(f"{course.title} | Dosen: {course.instructor.username} | Kategori: {course.category.name}")
        
        queries_optimized = len(connection.queries)
        self.stdout.write(self.style.SUCCESS(f'>> Total Database Query tereksekusi (Optimized): {queries_optimized}\n'))
        
       
        self.stdout.write(self.style.WARNING('--- KESIMPULAN PERBANDINGAN ---'))
        self.stdout.write(f"Untuk memuat 10 Course:")
        self.stdout.write(f"- Tanpa Optimasi (N+1) memakan  : {queries_n_plus_1} Queries (Sangat berat)")
        self.stdout.write(f"- Dengan select_related memakan : {queries_optimized} Query (Sangat ringan)")