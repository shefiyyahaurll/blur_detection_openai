# Blur Detection Project (Dockerized)

## 📌 Deskripsi Singkat
Project ini adalah aplikasi **Blur Detection** berbasis Python yang digunakan untuk:
- Menghitung **blur score** dari kumpulan gambar
- Menentukan apakah gambar **blur** atau **tidak blur**
- Menghasilkan **file CSV ringkasan** hasil analisis
- Dijalankan sepenuhnya menggunakan **Docker** (tanpa setup Python manual)


---

## 🗂️ Struktur Project

```
blur_detection_openai/
├── images/            # Folder input gambar (.jpg / .png)
├── output/            # Folder output (summary.csv)
├── .dockerignore
├── .env               # (opsional) environment variable
├── app.py             # Source code utama
├── Dockerfile         # Konfigurasi Docker
├── requirements.txt   # Dependency Python
```

---

## ⚙️ Teknologi yang Digunakan
- flask
- opencv-python-headless
- pandas
- openai


> ❗ Project ini **bergantung pada API eksternal** [link](https://openrouter.ai/openai/gpt-oss-20b:free/api)


---

## 🚀 Cara Menjalankan Project

### 1️⃣ Pastikan Docker Terinstall
Cek dengan:
```bash
docker --version
```

---

### 2️⃣ Build Docker Image
Dari folder project:
```bash
docker build -t blur-openai .
```

---

### 3️⃣ Jalankan Container
```bash
docker run -p 8000:8000 ^
-e OPENAI_API_KEY=sk-............... ^
-v C:\test\BLUR_DETECTION_OPENAI\images:/app/images ^
-v C:\test\BLUR_DETECTION_OPENAI\output:/app/output ^
blur-openai
```


---

## 📊 Output
Setelah container berjalan:
- File hasil akan otomatis dibuat di:
```
output/summary.csv
```



## 🧠 Cara Kerja Singkat
1. Program membaca semua gambar dari folder `images/`
2. Menghitung **variance of Laplacian** untuk blur score
3. Menentukan kategori:
   - Blur → skor kecil
   - Tidak blur → skor besar
4. Menyimpan hasil ke CSV
5. Menjalankan Flask server di port 8000

---

## 🧪 Kriteria Blur
Threshold blur dapat diatur di `app.py`:
```python
THRESHOLD = 100
```
        ┌──────────────┐
        │   Input Image│
        └──────┬───────┘
               ↓
      ┌──────────────────┐
      │ Convert to Gray  │
      └──────┬───────────┘
               ↓
      ┌──────────────────┐
      │ Apply Laplacian  │
      └──────┬───────────┘
               ↓
      ┌──────────────────┐
      │ Compute Variance │
      └──────┬───────────┘
               ↓
      ┌──────────────────────────┐
      │ blur_score < threshold ? │
      └──────┬───────────┬──────┘
             YES          NO
              ↓            ↓
        ┌─────────┐  ┌─────────────────┐
        │  BLUR   │  │ Call OpenAI API │
        └─────────┘  └────────┬────────┘
                                ↓
                       ┌─────────────────┐
                       │ Image Description│
                       └─────────────────┘


---


---

## 📌 Catatan Penting
- Pastikan folder `images` **tidak kosong**
- Format gambar: `.jpg`, `.jpeg`, `.png`
- Gunakan Docker Desktop (Windows / Mac)

---


✨ *Happy Coding!*
