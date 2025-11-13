# ⚡ GARUDA DOS TOOLKIT - UNLEASH THE ULTIMATE DOS DOMINATION ⚡

![Garuda - Logo](https://github.com/user-attachments/assets/33dfcfc3-e55c-4b47-aa70-5a7a3380a44d)

**Garuda DOS Toolkit** adalah sebuah perangkat canggih yang dirancang untuk melakukan pengujian stres dan simulasi serangan *Denial-of-Service* (DoS). Dibuat dengan Python menggunakan `asyncio`, toolkit ini menawarkan performa tinggi dan efisiensi dalam menjalankan serangan. Arsitekturnya yang modular memungkinkan pengembangan dan integrasi metode serangan baru dengan mudah, sementara fokus utamanya adalah pada teknik-teknik penghindaran (*evasion*) canggih untuk melewati sistem proteksi modern.

## Peringatan

⚠️ **HANYA UNTUK TUJUAN PENDIDIKAN & PENGUJIAN RESMI** ⚠️

Alat ini dibuat untuk membantu para profesional keamanan dan pengembang dalam menguji ketahanan infrastruktur mereka dalam lingkungan yang terkendali. Penggunaan alat ini untuk aktivitas ilegal atau menyerang target tanpa izin eksplisit adalah dilarang keras. **Pengembang tidak bertanggung jawab atas penyalahgunaan apa pun dari alat ini.**

## Fitur Utama

- **Serangan Multi-Metode**: Mendukung berbagai jenis serangan seperti `http-flood`, `slowloris`, dan mode `mixed` yang dapat menggabungkan beberapa serangan sekaligus.
- **Teknik Evasion Canggih**: Dilengkapi dengan modul untuk menghasilkan header HTTP yang realistis, *User-Agent* acak, dan *Referer* yang valid untuk menyamarkan lalu lintas serangan agar terlihat seperti aktivitas pengguna biasa.
- **Monitoring Real-Time**: Menyediakan statistik serangan secara langsung di terminal, termasuk durasi, koneksi aktif, paket terkirim, dan koneksi gagal.
- **Laporan Komprehensif**: Menampilkan laporan akhir yang detail setelah serangan selesai, mencakup total paket terkirim, rata-rata paket per detik, dan tingkat keberhasilan.
- **Konfigurasi Fleksibel**: Pengguna dapat dengan mudah mengatur parameter serangan seperti target, jumlah koneksi, durasi, dan mode `stealth` untuk serangan yang lebih lambat dan tidak terdeteksi.
- **Arsitektur Modular**: Desain yang bersih dan terstruktur memudahkan pengembang untuk menambahkan metode serangan atau teknik evasion baru.

## Instalasi

Untuk memulai, pastikan Anda memiliki Python 3.8+ terinstal.

1. **Clone repositori ini:**
   
   ```bash
   git clone https://github.com/RozhakXD/Garuda-DOS-Toolkit.git
   cd Garuda-DOS-Toolkit
   ```

2. **Instal dependensi yang diperlukan:**
   
   ```bash
   pip install -r requirements.txt
   ```

## Penggunaan

Gunakan perintah berikut untuk melihat semua opsi yang tersedia:

```bash
python main.py --help
```

**Sintaks Dasar:**

```
usage: main.py [-h] -t TARGET -m {http-flood,slowloris,mixed} [-c CONNECTIONS] [-d DURATION] [-s] [--attacks [ATTACKS ...]]

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET, --target TARGET
                        URL target (e.g., http://example.com)
  -m {http-flood,slowloris,mixed}, --method {http-flood,slowloris,mixed}
                        Metode serangan yang akan digunakan
  -c CONNECTIONS, --connections CONNECTIONS
                        Jumlah koneksi simultan (default: 100)
  -d DURATION, --duration DURATION
                        Durasi serangan dalam detik (default: 60)
  -s, --stealth         Aktifkan mode stealth (serangan lambat)
  --attacks [ATTACKS ...]
                        Sub-serangan untuk mode 'mixed' (e.g., http-flood slowloris)
```

### Contoh Perintah

- **Serangan HTTP Flood** dengan 500 koneksi selama 120 detik:
  
  ```bash
  python main.py -t http://example.com -m http-flood -c 500 -d 120
  ```

- **Serangan Slowloris** dengan 200 koneksi selama 300 detik ke target HTTPS:
  
  ```bash
  python main.py -t https://example.com -m slowloris -c 200 -d 300
  ```

- **Serangan Gabungan (Mixed)** yang mengkombinasikan `http-flood` dan `slowloris` dengan 250 koneksi selama 180 detik:
  
  ```bash
  python main.py -t http://example.com -m mixed --attacks http-flood slowloris -c 250 -d 180
  ```

## Metode Serangan

1. **HTTP Flood (`http-flood`)**
   Serangan ini membanjiri server dengan sejumlah besar permintaan HTTP(S). Garuda mengimplementasikan versi canggih yang menggunakan berbagai metode (`GET`, `POST`, dll.), header realistis, dan *path* yang bervariasi untuk meniru lalu lintas pengguna asli dan menghindari deteksi oleh WAF atau Cloudflare.

2. **Slowloris (`slowloris`)**
   Ini adalah serangan *low-and-slow* yang dirancang untuk menghabiskan sumber daya server. Serangan ini membuka banyak koneksi ke server dan menjaganya tetap terbuka selama mungkin dengan mengirimkan data parsial secara berkala. Hal ini secara perlahan melumpuhkan server tanpa memerlukan *bandwidth* yang besar.

3. **Mixed Attack (`mixed`)**
   Mode ini memungkinkan pengguna untuk meluncurkan beberapa jenis serangan secara bersamaan terhadap satu target. Ini menciptakan pola serangan yang kompleks dan tidak dapat diprediksi, sehingga lebih sulit untuk dimitigasi.

## Lisensi

Proyek ini dilisensikan di bawah [Lisensi MIT](LICENSE).