# Buku Tamu Digital Kampus (Digital Guestbook Wisuda)
> **Ujian Chunin — Cloud-Native Fullstack Application & Automated CI/CD Pipeline**  
> **Mata Kuliah:** Cloud Computing | **Dosen Pengampu:** CSO | **Telkom University**

---

## 👥 Identitas Anggota Kelompok
* **Developer 1 (Frontend & Gateway):** Hanifah Kamiliya Darmawan — 101012300127
* **Developer 2 (Backend & Data):** Putri Adinda Silvia — 101012300197
* **Developer 3 (DevOps, Infrastructure & Reliability - Lead):** Aldora Rian Perdana — 101012300289

---

## 📖 1. Deskripsi Studi Kasus
Proyek ini mengimplementasikan **Studi Kasus 1: Buku Tamu Digital Kampus** khusus untuk momentum perayaan wisuda Telkom University. Aplikasi dirancang berbasis arsitektur *cloud-native micro-services* yang mengisolasi antarmuka pengguna (*frontend*), pemroses logika dan data (*backend*), serta penyimpanan persisten (*storage volume*).

### Fitur Fungsional Utama:
1. **Dual-Role Form:** Formulir kontekstual untuk wisudawan (**Mahasiswa**: Nama, NIM, Fakultas, Program Studi) dan pendamping (**Orang Tua**: Nama Orang Tua, Nama Mahasiswa, Fakultas).
2. **Review & Rating System:** Pemberian nilai kepuasan bintang 1–5 dan ulasan pesan kesan wisuda.
3. **Photo Attachment:** Unggah 1 foto kenangan wisuda dengan kompresi otomatis berbasis *HTML5 Canvas*.
4. **Real-Time Clock & Header:** Jam digital real-time berstandar Waktu Indonesia Barat (WIB) dengan identitas visual Telkom University.
5. **Instant Deletion by ID:** Fitur penghapusan entri kunjungan secara real-time langsung ke server dengan modal konfirmasi dan notifikasi toast ceklis hijau.

---

## 🏛️ 2. Arsitektur Sistem & Containerization

Sistem menerapkan prinsip *separation of concerns*, *security hardening*, dan *data immunity*:

```text
[ Browser / Klien ]
        │
        │ HTTP Request (Port 8081 - Single Public Gateway)
        ▼
┌──────────────────────────────────────────────────────────────────┐
│ Docker Host Engine (Custom Bridge Network: appnet)               │
│                                                                  │
│  ┌───────────────────────────┐      ┌─────────────────────────┐  │
│  │   guestbook-frontend      │      │   guestbook-backend     │  │
│  │      (Nginx Alpine)       │ ───► │      (Python 3.11)      │  │
│  │ Port Host: 8081:8081      │/api/ │ Port Internal: 5000     │  │
│  │ User: nginx               │      │ User: appuser (UID 10001│)  │
│  └─────────────┬─────────────┘      └────────────┬────────────┘  │
│                │                                 │               │
│           Bind Mount                        Named Volume         │
│     (./frontend & ./nginx.conf)          (guestbook-db-data      │
│                                              pada /data)         │
│                                                  │               │
│                                            guestbook.json        │
│                                            (Atomic Write)        │
└──────────────────────────────────────────────────────────────────┘