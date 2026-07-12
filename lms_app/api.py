from .tasks import send_enrollment_email, export_course_report
from typing import List
from django.contrib.auth.hashers import make_password
from ninja import Schema
from ninja.pagination import paginate
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post, http_put, http_delete
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.authentication import JWTAuth
from .models import User, Course, Category, Enrollment, Progress
from .utils import redis_cache_page, rate_limiter, log_activity
from django.contrib.auth import authenticate
from ninja_jwt.tokens import RefreshToken
from celery.result import AsyncResult  # <-- Ini yang tadi belum di-import

from .schemas import (
    UserOut, RegisterIn, UpdateProfileIn, Message,
    CourseOut, CourseCreateIn, EnrollmentOut, ProgressOut, ProgressUpdateIn, LoginSchema
)

api = NinjaExtraAPI(title="Simple LMS API", version="1.0.0")

def is_role(user, role_name):
    return hasattr(user, 'role') and user.role == role_name

# ==========================================
# 1. DEKLARASI SCHEMAS TAMBAHAN
# ==========================================
class TaskStatusOut(Schema):
    task_id: str
    status: str
    result: str = None

class ExportOut(Schema):
    message: str
    task_id: str


# ==========================================
# 2. AUTH CONTROLLER
# ==========================================
@api_controller('/auth', tags=['Authentication'])
class AuthController:
    
    @http_post('/register', response={201: UserOut, 400: Message})
    def register(self, data: RegisterIn):
        if User.objects.filter(username=data.username).exists():
            return 400, {"message": "Username sudah dipakai"}
        
        user = User.objects.create(
            username=data.username,
            email=data.email,
            password=make_password(data.password),
            role=data.role
        )
        
        log_activity(
            user_id=user.id, 
            username=user.username, 
            action="REGISTER", 
            details=f"User terdaftar dengan role {user.role}"
        )
        
        return 201, user

    @http_get('/me', auth=JWTAuth(), response=UserOut)
    def me(self, request):
        return request.user

    @http_put('/me', auth=JWTAuth(), response=UserOut)
    def update_profile(self, request, data: UpdateProfileIn):
        user = request.user
        for attr, value in data.dict(exclude_unset=True).items():
            setattr(user, attr, value)
        user.save()
        return user


# ==========================================
# 3. COURSE CONTROLLER (Tadi ini hilang!)
# ==========================================
@api_controller('/courses', tags=['Courses'])
class CourseController:

    @http_post('/export-report', auth=JWTAuth(), response={202: ExportOut})
    def trigger_export(self, request):
        if not is_role(request.user, 'admin'):
            return 403, {"message": "Hanya Admin yang boleh mencetak laporan"}
        
        task = export_course_report.delay("laporan_terbaru_lms.csv")
        
        return 202, {
            "message": "Proses ekspor laporan sedang berjalan di latar belakang (Async)",
            "task_id": task.id 
        }
    
    @http_get('/tasks/{task_id}', response={200: TaskStatusOut, 404: dict})
    def get_task_status(self, request, task_id: str):
        task_result = AsyncResult(task_id)
        
        if task_result.status == 'PENDING' and not task_result.info:
            return 200, {"task_id": task_id, "status": "NOT_FOUND", "result": "Task ID tidak dikenali"}

        result_data = str(task_result.result) if task_result.ready() else None

        return 200, {
            "task_id": task_id,
            "status": task_result.status,
            "result": result_data
        }
    
    @http_get('/', response=List[CourseOut])
    @paginate
    # @rate_limiter(requests_limit=60)
    # @redis_cache_page(timeout=300)
    def list_courses(self):
        return Course.objects.for_listing()

    @http_get('/{course_id}', response=CourseOut)
    # @rate_limiter(requests_limit=60)
    # @redis_cache_page(timeout=300)
    def course_detail(self, request, course_id: int):
        try:
            return Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return 404, {"message": "Course tidak ditemukan"}

    @http_post('/', auth=JWTAuth(), response={201: CourseOut, 403: Message})
    def create_course(self, request, data: CourseCreateIn):
        if not is_role(request.user, 'instructor'):
            return 403, {"message": "Hanya Instructor yang boleh membuat course"}
        
        category = Category.objects.get(id=data.category_id)
        course = Course.objects.create(
            title=data.title,
            instructor=request.user,
            category=category
        )
        return 201, course

    @http_delete('/{course_id}', auth=JWTAuth(), response={200: Message, 403: Message})
    def delete_course(self, request, course_id: int):
        if not is_role(request.user, 'admin'):
            return 403, {"message": "Hanya Admin yang boleh menghapus course"}
        
        Course.objects.filter(id=course_id).delete()
        return 200, {"message": "Course berhasil dihapus"}

# Contoh saat ada user daftar atau event tertentu
from .tasks import send_email_task

def trigger_email_notification(email_tujuan):
    # Panggil dengan .delay() agar jadi ASYNC
    send_email_task.delay( 
        "Selamat Datang di LMS", 
        "Terima kasih telah bergabung!", 
        email_tujuan
    )
    
# ==========================================
# 4. ENROLLMENT CONTROLLER
# ==========================================
@api_controller('/enrollments', tags=['Enrollments'], auth=JWTAuth())
class EnrollmentController:
    
    @http_post('/', response={201: EnrollmentOut, 403: Message})
    def enroll(self, request, course_id: int):
        if not is_role(request.user, 'student'):
            return 403, {"message": "Hanya Student yang bisa mendaftar course"}
        
        course = Course.objects.get(id=course_id)
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user, 
            course=course
        )
        
        log_activity(
            user_id=request.user.id, 
            username=request.user.username, 
            action="ENROLL_COURSE", 
            details=f"Mendaftar ke course: {course.title}"
        )
        
        send_enrollment_email.delay(request.user.id, course.title)
        
        return 201, enrollment

    @http_get('/my-courses', response=List[EnrollmentOut])
    def my_courses(self, request):
        return Enrollment.objects.for_student_dashboard(request.user)

    @http_post('/{enrollment_id}/progress', response=ProgressOut)
    def update_progress(self, request, enrollment_id: int, lesson_id: int, data: ProgressUpdateIn):
        enrollment = Enrollment.objects.get(id=enrollment_id, student=request.user)
        progress, created = Progress.objects.update_or_create(
            enrollment=enrollment,
            lesson_id=lesson_id,
            defaults={'is_completed': data.is_completed}
        )
        return progress


# ==========================================
# 5. REGISTRASI CONTROLLER
# ==========================================
api.register_controllers(AuthController)
api.register_controllers(CourseController)
api.register_controllers(EnrollmentController)
api.register_controllers(NinjaJWTDefaultController)