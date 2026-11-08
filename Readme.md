# Buku Tamu Digital Kampus (Digital Guestbook Wisuda)
> Ujian Chunin - Cloud-Native Fullstack Application & Automated CI/CD Pipeline  
> **Mata Kuliah:** Cloud Computing | **Dosen:** CSO | **Telkom University**

---

## 👥 Identitas Anggota Kelompok
* **Developer 1 (Frontend & Gateway):** [Nama Rekan 1] - [NIM]
* **Developer 2 (Backend & Data):** [Nama Rekan 2] - [NIM]
* **Developer 3 (DevOps, Infrastructure & Reliability - Lead):** [Nama Anda] - [NIM Anda]

---

## 🏛️ Arsitektur Sistem & Containerization

```text
[ Browser / Klien ]
        │
        │ HTTP Port 8081 (Satu-satunya port publik)
        ▼
┌────────────────────────────────────────────────────────┐
│ Docker Host                                            │
│                                                        │
│  ┌──────────────────────┐      ┌────────────────────┐  │
│  │  guestbook-frontend  │      │ guestbook-backend  │  │
│  │     (Nginx:alpine)   │ ──── │   (Python 3.11)    │  │
│  │                      │/api/ │                    │  │
│  └──────────────────────┘      └─────────┬──────────┘  │
│             │                            │             │
│        Bind Mount                   Named Volume       │
│     (./index.html &             (guestbook-db-data     │
│       nginx.conf)                  pada /data)         │
│                                          │             │
│                                    guestbook.json      │
│                                    (Atomic Write)      │
│                                                        │
│                Network: appnet (Bridge)                │
└────────────────────────────────────────────────────────┘