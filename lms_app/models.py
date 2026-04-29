from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. User (dengan role)
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='student')

# 2. Category (self-referencing)
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

# Custom Manager untuk Course
class CourseManager(models.Manager):
    def for_listing(self):
        # Optimasi N+1 problem saat memanggil foreign key
        return self.select_related('instructor', 'category')

# 3. Course
class Course(models.Model):
    title = models.CharField(max_length=200)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'}, related_name='courses_taught')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    
    objects = CourseManager() # Pasang custom manager

    def __str__(self):
        return self.title

# 4. Lesson (dengan ordering)
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

# Custom Manager untuk Enrollment
class EnrollmentManager(models.Manager):
    def for_student_dashboard(self):
        # Optimasi query untuk dashboard student
        return self.select_related('course').prefetch_related('progress_set', 'progress_set__lesson')

# 5. Enrollment (dengan unique constraint)
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    objects = EnrollmentManager()

    class Meta:
        unique_together = ('student', 'course') # Unique constraint

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

# 6. Progress (tracking lesson completion)
class Progress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress_set')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('enrollment', 'lesson')

    def __str__(self):
        status = "Completed" if self.is_completed else "Pending"
        return f"{self.enrollment.student.username} - {self.lesson.title} ({status})"