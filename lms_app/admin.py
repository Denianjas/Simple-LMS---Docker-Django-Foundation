from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Category, Course, Lesson, Enrollment, Progress


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    
   
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1 


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category')
    search_fields = ('title', 'instructor__username')
    list_filter = ('category', 'instructor')
    inlines = [LessonInline] 


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('enrolled_at', 'course')
    search_fields = ('student__username', 'course__title')


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'lesson', 'is_completed')
    list_filter = ('is_completed',)
    search_fields = ('enrollment__student__username', 'lesson__title')


    def get_student_name(self, obj):
        return obj.enrollment.student.username
    get_student_name.short_description = 'Student'