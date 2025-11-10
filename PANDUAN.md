# Panduan Pengguna WiFi Toolkit (RATA)

Dokumen ini menyediakan panduan komprehensif untuk menggunakan semua fitur yang tersedia di program `wifiRATA`.

---

## Menu Utama

Saat program dijalankan, Anda akan disambut dengan menu utama yang berisi daftar semua fungsi yang tersedia.

### `[1] Network Scanning (airodump-ng)`

- **Tujuan:** Untuk memindai dan melihat jaringan WiFi serta perangkat (klien) di sekitar Anda.
- **Cara Menggunakan:**
    1. Pilih opsi `1`.
    2. Anda akan diberi dua pilihan:
        - **`1) Standard Scan`**: Hanya menampilkan jaringan dan klien di layar. Tekan `Ctrl+C` untuk berhenti dan kembali ke menu.
        - **`2) Scan and Save`**: Mirip seperti pemindaian standar, tetapi juga menyimpan semua paket yang ditangkap ke file `.cap` di direktori saat ini. Anda akan diminta memasukkan nama file untuk output.

### `[2] DoS Attacks (mdk4, aireplay)`

- **Tujuan:** Menu khusus untuk berbagai jenis serangan Denial-of-Service (DoS) untuk mengganggu jaringan.
- **Cara Menggunakan:**
    1. Pilih opsi `2`.
    2. Anda akan masuk ke sub-menu DoS:
        - **Opsi 1-4** adalah serangan standar (Jamming, PMKID, Deauth, Beacon) yang akan meminta Anda memasukkan **channel** dan **durasi** serangan.
        - **Opsi `[5] Smart Adaptive Attack`** adalah fitur paling canggih.

#### Detail: `[5] Smart Adaptive Attack`
- **Tujuan:** Meluncurkan serangan DoS cerdas yang dapat mengukur dampaknya sendiri dan secara otomatis menyesuaikan tingkat agresivitasnya.
- **Cara Menggunakan:**
    1. Pilih opsi `5` di menu DoS.
    2. Program akan memindai target yang memiliki klien aktif.
    3. Pilih AP target dari daftar.
    4. Program akan memulai serangan dalam mode 'stealthy' sambil terus memantau efektivitasnya (apakah klien benar-benar terputus).
    5. Jika tidak efektif, program akan secara otomatis beralih ke strategi yang lebih agresif hingga target berhasil diganggu.
    6. Tekan `Ctrl+C` untuk menghentikan serangan.

### `[3] Mass Deauthentication (mdk4)`

- **Tujuan:** Untuk meluncurkan serangan massal (area luas) tanpa perlu memilih target spesifik. Berguna untuk menciptakan gangguan umum.
- **Cara Menggunakan:**
    1. Pilih opsi `3`.
    2. Pilih jenis serangan:
        - **`1) Deauthentication Flood (Broadcast)`**: Mengirim paket deautentikasi ke semua perangkat di sekitar, menyebabkan gangguan koneksi massal.
        - **`2) Deauthentication Flood (From Target List)`**: Mirip seperti di atas, tetapi hanya menargetkan AP yang alamat MAC-nya ada di file `blacklist.txt`.
        - **`3) Beacon Flood (From SSID List)`**: Membuat ratusan hingga ribuan Access Point palsu. Nama AP palsu diambil dari file `ssidlist.txt`. Ini akan mengacaukan daftar jaringan WiFi di perangkat sekitar.
    3. Setelah memilih, serangan akan berjalan hingga Anda menghentikannya dengan `Ctrl+C`.

### `[4] Interactive Deauth (aireplay-ng)`

- **Tujuan:** Untuk serangan deautentikasi yang sangat spesifik, menargetkan satu AP dan satu atau semua klien yang terhubung padanya.
- **Cara Menggunakan:**
    1. Pilih opsi `4`.
    2. Program akan memindai jaringan selama 20 detik.
    3. Anda akan disajikan daftar AP yang ditemukan. Pilih nomor AP yang ingin Anda serang.
    4. Program kemudian akan menampilkan daftar klien yang terhubung ke AP tersebut.
    5. Anda dapat memilih untuk menyerang **satu klien spesifik** (dengan memilih nomornya) atau **semua klien** di AP tersebut (dengan menekan tombol `a`).
    6. Serangan akan berjalan terus menerus hingga dihentikan dengan `Ctrl+C`.

### `[5] Handshake Capture`

- **Tujuan:** Fitur paling efisien untuk menangkap Handshake WPA/WPA2 (diperlukan untuk cracking password).
- **Cara Menggunakan:**
    1. Pilih opsi `5`.
    2. Program akan memindai jaringan untuk mencari target yang menggunakan enkripsi WPA/WPA2.
    3. Pilih AP target dari daftar yang ditampilkan.
    4. Program akan bekerja **sepenuhnya otomatis**: menjalankan `airodump-ng` untuk mendengarkan, dan `aireplay-ng` untuk memancing klien agar terhubung kembali.
    5. Program akan memantau proses ini. Jika handshake berhasil ditangkap, serangan akan berhenti secara otomatis.
    6. **Hasil:** Path lengkap ke file `.cap` yang berisi handshake akan ditampilkan di layar. File disimpan di folder baru bernama `handshakes/`.

### `[6] Evil Twin Attack`

- **Tujuan:** Untuk membuat Access Point (AP) palsu yang meniru jaringan target, dengan tujuan memancing perangkat di sekitar untuk terhubung ke AP palsu Anda alih-alih yang asli. Ini memungkinkan Anda untuk memantau lalu lintas atau mengarahkan mereka ke halaman palsu.
- **Panduan Lengkap:** Untuk petunjuk penggunaan yang lebih detail, persyaratan, dan pertimbangan keamanan, lihat [Panduan Serangan Evil Twin](docs/evil_twin_guide.md).

### `[7] SQL Injection (sqlmap)`

- **Tujuan:** Menyediakan antarmuka otomatis untuk `sqlmap` guna menemukan dan mengeksploitasi kerentanan SQL injection di situs web.
- **Cara Menggunakan:**
    1. Pilih opsi `7` untuk masuk ke menu `sqlmap`.
    2. Anda akan disajikan beberapa opsi pemindaian:
        - **`1) Scan Single URL`**: Memindai URL spesifik untuk kerentanan dasar.
        - **`2) Auto-Discover & Scan Site`**: Merayapi seluruh situs web dari URL dasar untuk menemukan dan menguji semua tautan dan formulir.
        - **`3) Guided Dump (Wizard)`**: Fitur paling kuat. Memandu Anda langkah demi langkah: menemukan database, memilih database, menemukan tabel, memilih tabel, dan akhirnya membuang isinya. Sangat otomatis.
        - **`4-6)`**: Opsi untuk melakukan enumerasi manual database, tabel, atau membuang isi tabel.
        - **`7) Custom Scan`**: Memungkinkan Anda memasukkan flag `sqlmap` kustom untuk fleksibilitas penuh.
        - **`8) Get OS Shell`**: Mencoba mendapatkan shell sistem operasi di server target jika kerentanan memungkinkan.

### `[8] Network Mapper (nmap)`

- **Tujuan:** Melakukan pemindaian jaringan tingkat lanjut untuk penemuan host, identifikasi layanan, dan deteksi kerentanan.
- **Cara Menggunakan:**
    1. Pilih opsi `8` untuk masuk ke menu `nmap`.
    2. Masukkan target Anda (misalnya, `192.168.1.0/24` untuk seluruh jaringan Anda, atau `192.168.1.1` untuk satu perangkat).
    3. Pilih jenis pemindaian:
        - **`1) Quick Scan`**: Pemindaian sangat cepat untuk menemukan host aktif dan port terbuka yang paling umum.
        - **`2) Intense Scan`**: Pemindaian mendalam yang mencakup deteksi OS, deteksi versi layanan, dan menjalankan skrip default. Memberikan gambaran paling komprehensif tentang target.
        - **`3) Ping Scan`**: Hanya memeriksa host mana yang aktif di jaringan tanpa memindai port.
        - **`4) Vulnerability Scan`**: Menggunakan skrip `vulners` untuk memeriksa layanan yang berjalan terhadap database kerentanan yang diketahui (CVE). **Sangat direkomendasikan** untuk penilaian keamanan.
        - **`5) UDP Scan`**: Memindai port UDP yang terbuka.
        - **`6) Custom Scan`**: Memungkinkan Anda memasukkan flag `nmap` Anda sendiri untuk fleksibilitas penuh.

### `[9] Stealth Mode`

- **Tujuan:** Untuk mengaktifkan mode siluman guna menyamarkan serangan Anda.
- **Cara Menggunakan:**
    1. Pilih opsi `9` untuk masuk ke menu konfigurasi.
    2. Anda dapat mengatur tiga parameter:
        - **MAC Rotation Interval:** Seberapa sering alamat MAC Anda akan diubah secara otomatis.
        - **Channel Hopping Interval:** Seberapa sering program akan berpindah saluran WiFi.
        - **TX Power:** Mengatur kekuatan sinyal kartu WiFi Anda (lebih rendah lebih sulit dideteksi).
    3. Setelah konfigurasi, mode siluman akan aktif dan berjalan di latar belakang hingga Anda menonaktifkannya lagi dari menu yang sama.

### `[10] Bandwidth Limiter (evillimiter)`

- **Tujuan:** Untuk memantau, menganalisis, dan membatasi bandwidth (kecepatan internet) perangkat lain di jaringan lokal Anda.
- **Penting:** Fitur ini berjalan pada antarmuka jaringan yang terhubung (mode *managed*), bukan mode monitor.
- **Cara Menggunakan:**
    1. Pilih opsi `10`.
    2. Program akan mendeteksi antarmuka jaringan yang terhubung ke WiFi. Pilih salah satu.
    3. `evillimiter` akan dimulai. Gunakan perintah seperti `scan` untuk menemukan host, dan `limit <ID> <rate>` untuk membatasi kecepatan mereka.
    4. Gunakan perintah `help` di dalam `evillimiter` untuk melihat semua opsi yang tersedia.

### `[11] Geolocation Attack (Seeker)`

- **Tujuan:** Untuk menemukan lokasi geografis target secara akurat dengan cara mengirimkan sebuah tautan (link).
- **Cara Menggunakan:**
    1. Pilih opsi `11`.
    2. Program akan secara otomatis memeriksa dependensi yang diperlukan (`php`, `ssh`, `ngrok`). Jika ada yang kurang, Anda akan diberi tahu.
    3. Program akan memulai `ngrok` untuk membuat tunnel publik dan menjalankan server `php`.
    4. Sebuah URL publik (misalnya, `https://random-string.ngrok.io`) akan ditampilkan di layar Anda.
    5. **Tugas Anda adalah mengirim URL ini ke target** melalui media sosial, email, atau pesan.
    6. Ketika target membuka tautan tersebut dan menyetujui permintaan izin lokasi di browser mereka, data lokasi (termasuk lintang, bujur, akurasi, dan bahkan foto jika memungkinkan) akan muncul di terminal Anda.
    7. Tekan `Ctrl+C` untuk menghentikan serangan dan mematikan server.

### `[12] Exit`

- **Tujuan:** Untuk keluar dari program dengan aman.
- **Cara Menggunakan:** Pilih opsi `12`. Program akan secara otomatis:
    - Menghentikan semua proses serangan yang aktif.
    - Mengembalikan antarmuka WiFi Anda ke mode "managed" (normal).
    - Mengembalikan alamat MAC asli Anda.
    - Menghapus file-file sementara.
    - Menghasilkan laporan ringkasan sesi.
