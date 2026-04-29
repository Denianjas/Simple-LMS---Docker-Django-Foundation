from typing import List
from django.contrib.auth.hashers import make_password
from ninja.pagination import paginate
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post, http_put, http_delete
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.authentication import JWTAuth
from .models import User, Course, Category, Enrollment, Progress
from .schemas import (
    UserOut, RegisterIn, UpdateProfileIn, Message,
    CourseOut, CourseCreateIn, EnrollmentOut, ProgressOut, ProgressUpdateIn
)


api = NinjaExtraAPI(title="Simple LMS API", version="1.0.0")


def is_role(user, role_name):
    return hasattr(user, 'role') and user.role == role_name


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


@api_controller('/courses', tags=['Courses'])
class CourseController:
    
    @http_get('/', response=List[CourseOut])
    @paginate
    def list_courses(self, request):
       
        return Course.objects.for_listing()

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

# 6. Registrasi Semua Controller
api.register_controllers(AuthController)
api.register_controllers(CourseController)
api.register_controllers(EnrollmentController)
api.register_controllers(NinjaJWTDefaultController)