from ninja import Schema
from typing import Optional, List

# 1. User & Auth Schemas
class UserOut(Schema):
    id: int
    username: str
    email: str
    role: str

class RegisterIn(Schema):
    username: str
    password: str
    email: str
    role: str # student, instructor, atau admin

class UpdateProfileIn(Schema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

class Message(Schema):
    message: str

# 2. Category Schema
class CategoryOut(Schema):
    id: int
    name: str

# 3. Course Schemas (Didefinisikan SEBELUM Enrollment agar tidak NameError)
class CourseOut(Schema):
    id: int
    title: str
    instructor: UserOut
    category: Optional[CategoryOut]

    # Tambahkan ini di lms_app/schemas.py (Taruh di bawah CourseOut)

class LessonOut(Schema):
    id: int
    title: str
    content: str
    order: int

class LessonCreateIn(Schema):
    title: str
    content: str
    order: int = 0

class CourseCreateIn(Schema):
    title: str
    category_id: int

# 4. Enrollment Schemas
class EnrollmentOut(Schema):
    id: int
    course: CourseOut
    enrolled_at: str

# 5. Progress Schemas
class ProgressOut(Schema):
    id: int
    lesson_id: int
    is_completed: bool

class ProgressUpdateIn(Schema):
    is_completed: bool