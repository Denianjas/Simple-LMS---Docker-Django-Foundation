# AKUN DEMO

ADMIN
user : Admin123
pass : admin123

Istructor
user : dosen_web
pass : rahasia123

studen
user : eko
pass : eko123


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


## Progress 2: Simple LMS - Database Design & ORM Implementation

##  Screenshot Query N+1

![Django Query N+1](images/(N+1).png)

##  Screenshot Django ADMIN page

![Django ADMIN PAGE](images/ADMIN.png)


## Progress 3: REST API Implementation with Django Ninja and JWT

## screenshot API-DOC

![Django API-DOC](images/API-DOC.png)

## Screenshot POSTMAN

![Django POSTMAN](images/POSTMAN.png)

# Progress 4: Simple LMS - Redis, Celery & Monitoring
Penjelasan Environment Variables (.env)
Proyek ini membutuhkan konfigurasi environment variables tambahan untuk Redis, RabbitMQ, dan MongoDB. Berikut adalah penjelasan untuk variabel baru tersebut:

REDIS_URL : Alamat koneksi ke Redis untuk keperluan caching (biasanya redis://redis:6379/1).

CELERY_BROKER_URL : URL message broker yang digunakan oleh Celery, yaitu RabbitMQ (amqp://guest:guest@rabbitmq:5672/).

MONGO_URI : String koneksi untuk menyimpan activity logs ke database MongoDB.

## Arsitektur Sistem
![DJANGO mermaid](images/mermaid.png)

## Caching Strategy
Sistem menggunakan pola Cache-Aside. Data yang diminta dari database akan disimpan ke Redis dengan TTL (Time-To-Live) selama 300 detik. Ini memastikan performa API tetap cepat dan mengurangi beban database pada request berulang.

## Task Flow
Proses berat seperti export report dijalankan secara asynchronous menggunakan Celery. API mengirim pesan tugas ke RabbitMQ, yang kemudian diproses oleh Celery Worker. Hal ini mencegah pemblokiran pada main thread API dan meningkatkan skalabilitas sistem.

## flowers

![DJANGO flowers](images/flowers.png)

## redis

![DJANGO redis](images/redis.png)


## Paket 6: Async Processing & Notification
Proyek ini mengimplementasikan pemrosesan tugas latar belakang (*background task*) dan sistem notifikasi otomatis menggunakan Celery, RabbitMQ, dan Redis.

### Fitur Terimplementasi
*   **Email Notification Async**: Pengiriman email dilakukan di latar belakang tanpa memblokir *request* utama.
*   **Report Generation Async**: Pembuatan laporan dalam format CSV diproses secara asinkron.
*   **Task Status Endpoint**: Memungkinkan pengguna melacak status tugas melalui `/tasks/{task_id}`.
*   **Scheduled Task (Celery Beat)**: Otomatisasi pembersihan data progres lama dilakukan setiap 1 menit.
*   **Flower Monitoring**: Dashboard *real-time* untuk memantau performa *worker* dan *task*.

### Demonstrasi & Verifikasi
Berikut adalah panduan cara memverifikasi fitur Paket 6 yang telah berjalan:

1.  **Monitor Task via Flower**:
    *   Akses dashboard di `http://localhost:5555`.
    *   Buka tab **Tasks** untuk melihat daftar tugas yang sudah diproses atau sedang berjalan.

2.  **Verifikasi Scheduled Task**:
    *   Periksa log `celery-worker` untuk melihat eksekusi otomatis:
        `docker compose logs -f celery-worker`
    *   Anda akan melihat log: `[... INFO/ForkPoolWorker-x] Sedang membersihkan data lama secara otomatis...` setiap 60 detik.

3.  **Cek Status Tugas via API**:
    *   Lakukan `POST` ke endpoint pembuatan laporan.
    *   Gunakan `task_id` yang didapat untuk mengecek status di endpoint `/tasks/{task_id}`.

    ## Generate report/cert async
      ![DJANGO certasync](images/certasync.png)
    ## Scheduled task
   ![DJANGO schedule](images/schedule.png)
    ## Task status endpoint

   ![DJANGO reportasync](images/reportasync.png)

    ## Flower monitoring

   ![DJANGO flower1](images/flower1.png)

   ## Email notification async

   ![DJANGO async1](images/async1.png)

    

    