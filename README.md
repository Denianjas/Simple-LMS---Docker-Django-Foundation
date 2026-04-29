# Progress 1: Simple LMS - Docker & Django Setup

## Penjelasan Environment Variables (.env)

Proyek ini membutuhkan konfigurasi environment variables agar dapat berjalan. Anda bisa menggunakan file `.env.example` sebagai acuan untuk membuat file `.env`. Berikut adalah penjelasan untuk masing-masing variabel:

* `POSTGRES_DB`: Nama database PostgreSQL yang akan digunakan secara otomatis oleh container database.
* `POSTGRES_USER`: Username untuk otentikasi ke dalam database PostgreSQL.
* `POSTGRES_PASSWORD`: Password yang dipasangkan dengan username database di atas.
* `POSTGRES_HOST`: Hostname tempat database berjalan. Di Docker Compose ini, nilainya diatur ke `db` (merujuk pada nama service).
* `POSTGRES_PORT`: Port yang digunakan oleh PostgreSQL untuk komunikasi jaringan (default: 5432).
* `DJANGO_SECRET_KEY`: Kunci kriptografi rahasia yang digunakan oleh instalasi Django.
* `DJANGO_DEBUG`: Variabel boolean untuk mengontrol mode debug Django (`True` untuk development, `False` untuk production).

## Cara Menjalankan Project

Berikut adalah langkah-langkah untuk melakukan instalasi dan menjalankan project ini secara lokal:

1. Buka terminal dan arahkan ke dalam folder direktori project (`simple-lms`).
2. Gandakan file konfigurasi environment:
   ```bash
   cp .env.example .env
3. docker-compose up -d --build
4. Lakukan migrasi database untuk membuat tabel bawaan Django di PostgreSQL:
   ```bash
   docker-compose exec web python manage.py migrate
5. Akses aplikasi melalui web browser di alamat:
    http://localhost:8000

##  Screenshot Django welcome page

![Django Welcome Page](images/DJANGO.png)


