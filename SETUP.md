# Cara memasang profil ini

## 1. Siapkan repo profil
Repo profil GitHub harus **bernama sama persis dengan username kamu** dan bersifat **Public**.
Contoh: username `budi` berarti repo `budi/budi`. Kalau repo itu sudah ada (README lama kamu), pakai yang itu.

## 2. Unggah file
Salin semua isi folder ini ke repo: `README.md`, folder `assets/`, `scripts/`, dan `.github/`.

Folder `.github` tersembunyi di Mac (tekan Cmd + Shift + titik di Finder untuk menampilkannya), dan upload lewat browser sering melewatkannya. Cara paling aman lewat terminal:

```
git clone https://github.com/USERNAME/USERNAME
cd USERNAME
# salin semua isi folder ini ke sini, lalu:
git add -A
git commit -m "feat: redesign profile"
git push
```

## 3. Ganti username di link proyek
Tiga link proyek di `README.md` masih berisi `GANTI_DENGAN_USERNAME_KAMU`. Ganti dengan username kamu:

```
sed -i '' 's/GANTI_DENGAN_USERNAME_KAMU/USERNAME/g' README.md
```

Nama repo proyek (`plantpal`, `lulc-badung`, `harvest-hub`) juga sesuaikan kalau berbeda.

## 4. Jalankan update statistik pertama
Total repo, grafik contribution, dan bahasa dibuat oleh GitHub Actions, bukan layanan pihak ketiga, jadi tidak ada kartu yang tiba-tiba mati.

1. Buka tab **Actions** di repo, lalu aktifkan kalau diminta.
2. Pilih **Update profile stats**, lalu klik **Run workflow**.
3. Tunggu sekitar satu menit. Setelah hijau, buka profilmu dan muat ulang.

Sesudah itu statistik diperbarui otomatis setiap 6 jam. Sebelum run pertama, kartunya menampilkan tanda "—".

Kalau workflow gagal saat push, buka **Settings > Actions > General > Workflow permissions** dan pilih **Read and write permissions**.

## 5. (Opsional) Hitung repo dan contribution privat
Secara bawaan hanya data publik yang terhitung. Supaya yang privat ikut:
1. Buat token di **Settings > Developer settings > Personal access tokens (classic)** dengan scope `read:user` dan `repo`.
2. Di repo profil, buka **Settings > Secrets and variables > Actions**, buat secret bernama `GH_PAT`, lalu tempel tokennya.
3. Di profil GitHub kamu, aktifkan **Include private contributions on my profile**.

Jumlah repo dan commit privat hanya angka, tidak ada nama repo yang tampil.

## Mengubah teks atau desain
- Teks di banner, ringkasan, tech stack, dan kartu proyek ada di `scripts/build_static.py` (bagian atas tiap fungsi). Ubah, lalu jalankan `python3 scripts/build_static.py` dan commit hasilnya di `assets/`.
- Warna ada di baris palet di bagian atas kedua skrip.
- Font memakai SF Pro di perangkat Apple. Di Windows dan Linux otomatis memakai font sistem, jadi tampilannya sedikit berbeda.
