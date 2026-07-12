from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

DB_PATH = Path(os.getenv("AUDORE_DB_PATH", Path(__file__).with_name("audore.db")))
VALID_ROLES = {"Caregiver", "Tenaga Medis", "Admin"}
VALID_MEDICAL_ROLES = {"", "Psikolog", "Dokter Spesialis Kedokteran Jiwa"}
VALID_CONSULTATION_STATUSES = {"Terjadwal", "Selesai", "Dibatalkan"}


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def _add_column_if_missing(
    conn: sqlite3.Connection,
    table: str,
    column: str,
    definition: str,
) -> None:
    if column not in _columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    )
    return salt.hex(), digest.hex()


def _verify_password(password: str, salt_hex: str, digest_hex: str) -> bool:
    try:
        salt = bytes.fromhex(salt_hex)
    except (TypeError, ValueError):
        return False
    _, candidate = _hash_password(password, salt)
    return secrets.compare_digest(candidate, digest_hex or "")


def init_db() -> None:
    """Create and migrate all SQLite tables used by Audore."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id_user INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT,
                password_salt TEXT,
                role TEXT NOT NULL,
                medical_role TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Backward-compatible migration for an older users table.
        _add_column_if_missing(conn, "users", "password_hash", "TEXT")
        _add_column_if_missing(conn, "users", "password_salt", "TEXT")
        _add_column_if_missing(conn, "users", "medical_role", "TEXT DEFAULT ''")
        _add_column_if_missing(conn, "users", "created_at", "TEXT")
        conn.execute(
            "UPDATE users SET created_at = COALESCE(created_at, ?) ",
            (_now(),),
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id_message INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                session_id TEXT NOT NULL,
                session_title TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                clean_text TEXT,
                kategori_output TEXT,
                kategori_masalah TEXT,
                recommended_feature TEXT,
                matched_keywords TEXT,
                skor_urgensi INTEGER,
                crisis_flag TEXT,
                scores TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_chat_user_session "
            "ON chat_messages(user_name, session_id, id_message)"
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS consultations (
                id_consultation INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_user_id INTEGER,
                patient_name TEXT NOT NULL,
                service_type TEXT NOT NULL,
                professional_name TEXT NOT NULL,
                consultation_date TEXT NOT NULL,
                consultation_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Terjadwal',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_user_id) REFERENCES users(id_user)
                    ON DELETE SET NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_consultation_service "
            "ON consultations(service_type, consultation_date, consultation_time)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_consultation_patient "
            "ON consultations(patient_user_id, consultation_date, consultation_time)"
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS community_posts (
                id_post INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_name TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                likes INTEGER NOT NULL DEFAULT 0,
                is_seed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id_user)
                    ON DELETE SET NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS community_replies (
                id_reply INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER,
                user_name TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES community_posts(id_post)
                    ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id_user)
                    ON DELETE SET NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS group_messages (
                id_group_message INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_name TEXT NOT NULL,
                message TEXT NOT NULL,
                is_bot INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id_user)
                    ON DELETE SET NULL
            )
            """
        )

        _seed_community(conn)
        conn.commit()


def _seed_community(conn: sqlite3.Connection) -> None:
    post_count = conn.execute("SELECT COUNT(*) AS n FROM community_posts").fetchone()["n"]
    if post_count == 0:
        first = conn.execute(
            """
            INSERT INTO community_posts
                (user_name, category, content, likes, is_seed, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (
                "Diandra A",
                "Gangguan Psikologis Pendamping",
                "Saya merasa kelelahan mendampingi terapi anak setiap hari. Apakah ada yang mengalami hal serupa?",
                3,
                _now(),
            ),
        )
        first_id = int(first.lastrowid)
        conn.execute(
            """
            INSERT INTO community_replies
                (post_id, user_name, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                first_id,
                "Anastasia",
                "Saya juga pernah mengalami hal yang sama.",
                _now(),
            ),
        )
        conn.execute(
            """
            INSERT INTO community_posts
                (user_name, category, content, likes, is_seed, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (
                "Dirga",
                "Kebutuhan Informasi",
                "Ada yang memiliki pengalaman mengenai terapi wicara untuk anak ASD?",
                2,
                _now(),
            ),
        )

    chat_count = conn.execute("SELECT COUNT(*) AS n FROM group_messages").fetchone()["n"]
    if chat_count == 0:
        defaults = [
            ("Amanda", "Hai semuanya! Ada yang punya tips agar anak lebih fokus saat belajar?"),
            ("Sabrina", "Halo, saya biasanya membuat jadwal belajar singkat lalu diselingi istirahat."),
            ("Hani", "Kalau saya biasanya membuat rutinitas yang konsisten untuk anak saya."),
        ]
        conn.executemany(
            """
            INSERT INTO group_messages
                (user_name, message, is_bot, created_at)
            VALUES (?, ?, 0, ?)
            """,
            [(name, message, _now()) for name, message in defaults],
        )


# ---------------------------------------------------------------------------
# Users and admin management
# ---------------------------------------------------------------------------

def register_user(
    nama: str,
    password: str,
    role: str,
    medical_role: str = "",
) -> tuple[bool, str]:
    init_db()
    nama = (nama or "").strip()
    role = (role or "").strip()
    medical_role = (medical_role or "").strip()

    if not nama or not password:
        return False, "Nama dan password harus diisi."
    if role not in VALID_ROLES:
        return False, "Jenis akun tidak valid."
    if role == "Tenaga Medis" and medical_role not in VALID_MEDICAL_ROLES - {""}:
        return False, "Jenis tenaga medis harus dipilih."
    if role != "Tenaga Medis":
        medical_role = ""

    salt, digest = _hash_password(password)
    try:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO users
                    (nama, password_hash, password_salt, role, medical_role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (nama, digest, salt, role, medical_role, _now()),
            )
            conn.commit()
        return True, "Akun berhasil dibuat."
    except sqlite3.IntegrityError:
        return False, "Nama pengguna sudah terdaftar."


def login_user(nama: str, password: str, role: str) -> tuple[bool, dict[str, Any] | None]:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE nama = ? COLLATE NOCASE AND role = ?",
            ((nama or "").strip(), role),
        ).fetchone()
        if row is None:
            return False, None

        data = dict(row)
        valid = False
        if data.get("password_hash") and data.get("password_salt"):
            valid = _verify_password(password, data["password_salt"], data["password_hash"])
        elif "password" in data:
            # Compatibility with an old database that stored a plain-text password.
            valid = secrets.compare_digest(str(data.get("password", "")), password)
            if valid:
                salt, digest = _hash_password(password)
                conn.execute(
                    "UPDATE users SET password_hash = ?, password_salt = ? WHERE id_user = ?",
                    (digest, salt, data["id_user"]),
                )
                conn.commit()

        if not valid:
            return False, None

        data.pop("password_hash", None)
        data.pop("password_salt", None)
        data.pop("password", None)
        return True, data


def get_all_users() -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id_user, nama, role, COALESCE(medical_role, '') AS medical_role,
                   created_at
            FROM users
            ORDER BY id_user ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def count_users_by_role(role: str) -> int:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM users WHERE role = ?",
            (role,),
        ).fetchone()
    return int(row["n"])


def update_user(
    user_id: int,
    nama: str,
    role: str,
    medical_role: str = "",
    new_password: str = "",
) -> tuple[bool, str]:
    init_db()
    nama = (nama or "").strip()
    role = (role or "").strip()
    medical_role = (medical_role or "").strip()

    if not nama:
        return False, "Nama pengguna tidak boleh kosong."
    if role not in VALID_ROLES:
        return False, "Jenis akun tidak valid."
    if role == "Tenaga Medis" and medical_role not in VALID_MEDICAL_ROLES - {""}:
        return False, "Jenis tenaga medis harus dipilih."
    if role != "Tenaga Medis":
        medical_role = ""

    try:
        with _connect() as conn:
            existing = conn.execute(
                "SELECT id_user FROM users WHERE id_user = ?",
                (int(user_id),),
            ).fetchone()
            if existing is None:
                return False, "Akun tidak ditemukan."

            if new_password:
                salt, digest = _hash_password(new_password)
                conn.execute(
                    """
                    UPDATE users
                    SET nama = ?, role = ?, medical_role = ?,
                        password_hash = ?, password_salt = ?
                    WHERE id_user = ?
                    """,
                    (nama, role, medical_role, digest, salt, int(user_id)),
                )
            else:
                conn.execute(
                    """
                    UPDATE users
                    SET nama = ?, role = ?, medical_role = ?
                    WHERE id_user = ?
                    """,
                    (nama, role, medical_role, int(user_id)),
                )
            conn.commit()
        return True, "Data akun berhasil diperbarui."
    except sqlite3.IntegrityError:
        return False, "Nama pengguna sudah digunakan oleh akun lain."


def delete_user(user_id: int) -> tuple[bool, str]:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT id_user FROM users WHERE id_user = ?",
            (int(user_id),),
        ).fetchone()
        if row is None:
            return False, "Akun tidak ditemukan."
        conn.execute("DELETE FROM users WHERE id_user = ?", (int(user_id),))
        conn.commit()
    return True, "Akun berhasil dihapus."


# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

def save_chat_message(
    *,
    user_name: str,
    session_id: str,
    session_title: str,
    role: str,
    content: str,
    clean_text: str | None = None,
    kategori_output: str | None = None,
    kategori_masalah: str | None = None,
    recommended_feature: str | None = None,
    matched_keywords: Iterable[str] | None = None,
    skor_urgensi: int | None = None,
    crisis_flag: str | None = None,
    scores: dict[str, Any] | None = None,
) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO chat_messages (
                user_name, session_id, session_title, role, content, clean_text,
                kategori_output, kategori_masalah, recommended_feature,
                matched_keywords, skor_urgensi, crisis_flag, scores, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_name,
                session_id,
                session_title,
                role,
                content,
                clean_text,
                kategori_output,
                kategori_masalah,
                recommended_feature,
                json.dumps(list(matched_keywords or []), ensure_ascii=False),
                skor_urgensi,
                crisis_flag,
                json.dumps(scores or {}, ensure_ascii=False),
                _now(),
            ),
        )
        conn.commit()


def load_chat_sessions(user_name: str) -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM chat_messages
            WHERE user_name = ?
            ORDER BY id_message ASC
            """,
            (user_name,),
        ).fetchall()

    sessions: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for raw in rows:
        row = dict(raw)
        session_id = row["session_id"]
        session = sessions.setdefault(
            session_id,
            {
                "id": session_id,
                "title": row["session_title"] or "Chat baru",
                "messages": [],
                "created_at": row["created_at"],
                "updated_at": row["created_at"],
            },
        )
        message: dict[str, Any] = {
            "role": row["role"],
            "content": row["content"],
        }
        if row.get("kategori_masalah") or row.get("kategori_output"):
            message["prediction_label"] = row.get("kategori_masalah") or row.get("kategori_output")
            message["recommended_feature"] = row.get("recommended_feature")
            message["skor_urgensi"] = row.get("skor_urgensi")
            message["crisis_flag"] = row.get("crisis_flag")
            try:
                message["matched_keywords"] = json.loads(row.get("matched_keywords") or "[]")
            except json.JSONDecodeError:
                message["matched_keywords"] = []
            try:
                stored_scores = json.loads(row.get("scores") or "{}")
            except json.JSONDecodeError:
                stored_scores = {}
            message["scores"] = stored_scores
            if isinstance(stored_scores, dict):
                message["probabilities"] = stored_scores.get("probabilities", {})
        session["messages"].append(message)
        session["title"] = row["session_title"] or session["title"]
        session["updated_at"] = row["created_at"]

    return list(reversed(list(sessions.values())))


def delete_chat_history(user_name: str) -> None:
    init_db()
    with _connect() as conn:
        conn.execute("DELETE FROM chat_messages WHERE user_name = ?", (user_name,))
        conn.commit()


# ---------------------------------------------------------------------------
# Consultations
# ---------------------------------------------------------------------------

def _normalize_optional_user_id(user_id: int | str | None) -> int | None:
    if user_id in (None, ""):
        return None
    try:
        return int(user_id)
    except (TypeError, ValueError):
        return None


def create_consultation(
    *,
    patient_user_id: int | None,
    patient_name: str,
    service_type: str,
    professional_name: str,
    consultation_date: str,
    consultation_time: str,
) -> int:
    """Save one consultation booking permanently in audore.db."""
    init_db()

    patient_name = (patient_name or "").strip()
    service_type = (service_type or "").strip()
    professional_name = (professional_name or "").strip()
    consultation_date = str(consultation_date or "").strip()
    consultation_time = str(consultation_time or "").strip()
    normalized_user_id = _normalize_optional_user_id(patient_user_id)

    if not patient_name:
        raise ValueError("Nama pasien tidak boleh kosong.")
    if not service_type:
        raise ValueError("Jenis layanan tidak boleh kosong.")
    if not professional_name:
        raise ValueError("Tenaga profesional tidak boleh kosong.")
    if not consultation_date or not consultation_time:
        raise ValueError("Tanggal dan jam konsultasi harus dipilih.")

    with _connect() as conn:
        # A stale session-state ID must not make the booking fail.
        if normalized_user_id is not None:
            existing_user = conn.execute(
                "SELECT id_user FROM users WHERE id_user = ?",
                (normalized_user_id,),
            ).fetchone()
            if existing_user is None:
                normalized_user_id = None

        cursor = conn.execute(
            """
            INSERT INTO consultations (
                patient_user_id, patient_name, service_type, professional_name,
                consultation_date, consultation_time, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'Terjadwal', ?)
            """,
            (
                normalized_user_id,
                patient_name,
                service_type,
                professional_name,
                consultation_date,
                consultation_time,
                _now(),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_consultations(
    *,
    service_type: str | None = None,
    patient_user_id: int | None = None,
    patient_name: str | None = None,
    professional_name: str | None = None,
) -> list[dict[str, Any]]:
    """Load consultation records with optional caregiver or medical filters."""
    init_db()
    clauses: list[str] = []
    params: list[Any] = []

    service_type = (service_type or "").strip()
    patient_name = (patient_name or "").strip()
    professional_name = (professional_name or "").strip()
    normalized_user_id = _normalize_optional_user_id(patient_user_id)

    if service_type:
        clauses.append("service_type = ?")
        params.append(service_type)

    if normalized_user_id is not None and patient_name:
        # Include legacy rows that may have been saved without patient_user_id.
        clauses.append(
            "(patient_user_id = ? OR "
            "(patient_user_id IS NULL AND patient_name = ? COLLATE NOCASE))"
        )
        params.extend([normalized_user_id, patient_name])
    elif normalized_user_id is not None:
        clauses.append("patient_user_id = ?")
        params.append(normalized_user_id)
    elif patient_name:
        clauses.append("patient_name = ? COLLATE NOCASE")
        params.append(patient_name)

    if professional_name:
        clauses.append("professional_name = ? COLLATE NOCASE")
        params.append(professional_name)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    with _connect() as conn:
        rows = conn.execute(
            f"""
            SELECT id_consultation,
                   patient_user_id,
                   patient_name AS 'Nama Pasien',
                   service_type AS 'Layanan',
                   professional_name AS 'Tenaga Profesional',
                   consultation_date AS 'Tanggal',
                   consultation_time AS 'Jam',
                   status AS 'Status',
                   created_at AS 'Dibuat Pada'
            FROM consultations
            {where}
            ORDER BY consultation_date ASC,
                     consultation_time ASC,
                     id_consultation DESC
            """,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def update_consultation_status(consultation_id: int, status: str) -> bool:
    """Update a consultation status and report whether a row was changed."""
    init_db()
    status = (status or "").strip()
    if status not in VALID_CONSULTATION_STATUSES:
        raise ValueError("Status konsultasi tidak valid.")

    with _connect() as conn:
        cursor = conn.execute(
            "UPDATE consultations SET status = ? WHERE id_consultation = ?",
            (status, int(consultation_id)),
        )
        conn.commit()
        return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Community
# ---------------------------------------------------------------------------

def get_community_posts() -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        posts = conn.execute(
            """
            SELECT id_post, user_id, user_name, category, content, likes,
                   is_seed, created_at
            FROM community_posts
            ORDER BY id_post DESC
            """
        ).fetchall()

        result: list[dict[str, Any]] = []
        for raw in posts:
            post = dict(raw)
            replies = conn.execute(
                """
                SELECT id_reply, user_id, user_name, content, created_at
                FROM community_replies
                WHERE post_id = ?
                ORDER BY id_reply ASC
                """,
                (post["id_post"],),
            ).fetchall()
            result.append(
                {
                    "id": post["id_post"],
                    "user_id": post["user_id"],
                    "nama": post["user_name"],
                    "kategori": post["category"],
                    "isi": post["content"],
                    "likes": int(post["likes"]),
                    "user_post": not bool(post["is_seed"]),
                    "created_at": post["created_at"],
                    "replies": [
                        {
                            "id": reply["id_reply"],
                            "user_id": reply["user_id"],
                            "nama": reply["user_name"],
                            "isi": reply["content"],
                            "created_at": reply["created_at"],
                        }
                        for reply in replies
                    ],
                }
            )
    return result


def create_community_post(
    *, user_id: int | None, user_name: str, category: str, content: str
) -> int:
    init_db()
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO community_posts
                (user_id, user_name, category, content, likes, is_seed, created_at)
            VALUES (?, ?, ?, ?, 0, 0, ?)
            """,
            (user_id, user_name, category, content, _now()),
        )
        conn.commit()
        return int(cursor.lastrowid)


def delete_community_post(post_id: int, user_id: int | None = None) -> bool:
    init_db()
    with _connect() as conn:
        if user_id is None:
            cursor = conn.execute(
                "DELETE FROM community_posts WHERE id_post = ?",
                (int(post_id),),
            )
        else:
            cursor = conn.execute(
                "DELETE FROM community_posts WHERE id_post = ? AND user_id = ?",
                (int(post_id), int(user_id)),
            )
        conn.commit()
        return cursor.rowcount > 0


def add_post_like(post_id: int) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "UPDATE community_posts SET likes = likes + 1 WHERE id_post = ?",
            (int(post_id),),
        )
        conn.commit()


def create_community_reply(
    *, post_id: int, user_id: int | None, user_name: str, content: str
) -> int:
    init_db()
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO community_replies
                (post_id, user_id, user_name, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (int(post_id), user_id, user_name, content, _now()),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_group_messages() -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id_group_message, user_id, user_name, message, is_bot, created_at
            FROM group_messages
            ORDER BY id_group_message ASC
            """
        ).fetchall()
    return [
        {
            "id": row["id_group_message"],
            "user_id": row["user_id"],
            "nama": row["user_name"],
            "pesan": row["message"],
            "bot": bool(row["is_bot"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def create_group_message(
    *, user_id: int | None, user_name: str, message: str, is_bot: bool = False
) -> int:
    init_db()
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO group_messages
                (user_id, user_name, message, is_bot, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, user_name, message, 1 if is_bot else 0, _now()),
        )
        conn.commit()
        return int(cursor.lastrowid)
