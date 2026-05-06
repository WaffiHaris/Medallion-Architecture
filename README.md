## Implementasi Medallion Architecture dengan MinIO

Project ini merupakan implementasi sederhana dari **Medallion Architecture (Bronze → Silver → Gold)** menggunakan **MinIO** dan **Python**.

---

##  Penjelasan

Medallion Architecture membagi data menjadi 3 bagian:

* **Bronze** → data mentah (file asli)
* **Silver** → data yang sudah dirapikan (metadata)
* **Gold** → data siap analisis

##  Tools yang Digunakan

* Python
* boto3
* pandas
* MinIO
* Parquet


## 🚀 Cara Menjalankan

### 1. Jalankan MinIO

```bash
minio server ~/minio-data \
  --console-address ":9001" \
  --license ~/Documents/minio/minio.license
```

Buka di browser:

```
http://127.0.0.1:9001
```

Login

---

### 2. Buat Bucket

Buat 3 bucket:

* bronze
* silver
* gold

### 3. Upload File ke Bronze

Upload minimal 10 file dengan format nama:

```
NRP_Nama_Tugas.ext
```

Contoh:

```
5026241000_Ahmad_Quiz1.pdf
```

### 4. Install Library

```bash
pip install boto3 pandas pyarrow
```

### 5. Jalankan Program

```bash
python3 medallion_pipeline.py
```

##  Alur Proses

### 🥉 Bronze

* Menyimpan file mentah (pdf, jpg, dll)

### 🥈 Silver

* Mengambil metadata dari file
* Memecah nama file (NRP, Nama, Tugas)
* Menyimpan ke CSV

### 🥇 Gold

* Menambahkan kategori ukuran file (Large / Small)
* Mengubah ke format Parquet


##  Hasil Analisis

Program akan menampilkan:

* Jumlah file berdasarkan tipe (pdf, jpg, dll)
* Daftar mahasiswa dengan file besar
* Rata-rata ukuran file


##  Output

* File CSV di bucket **silver**
* File Parquet di bucket **gold**
* Screenshot bucket (bronze, silver, gold)


##  Identitas

* Nama: Waffi Haris Ashari
* Mata Kuliah: Data Lakehouse

---
