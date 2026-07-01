from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Course

@receiver([post_save, post_delete], sender=Course)
def clear_course_cache(sender, instance, **kwargs):
    """Otomatis menghapus cache di Redis jika data Course berubah atau dihapus"""
    # Hapus cache untuk list courses
    cache.delete("cache_/api/courses/_")
    # Hapus cache untuk detail course yang bersangkutan
    cache.delete(f"cache_/api/courses/{instance.id}_{instance.id}")
    print("Redis Cache untuk Course berhasil dibersihkan otomatis!")