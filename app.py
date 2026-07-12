import html

import streamlit as st
import pandas as pd

from database import (
    init_db,
    register_user as db_register_user,
    login_user as db_login_user,
    get_all_users,
    delete_user as db_delete_user,
)

from edukasi import run_edukasi
from komunitas import run_komunitas
from konsultasi import run_konsultasi
from ml_app import run_ml_app


# ======================
# Page Configuration
# ======================
st.set_page_config(
    page_title="Audore",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Database SQLite dibuat otomatis saat aplikasi dijalankan.
init_db()


# ======================
# Constants
# ======================
USER_TYPES = ["Caregiver", "Tenaga Medis", "Admin"]

MEDICAL_ROLE_PLACEHOLDER = "Pilih jenis tenaga medis"
MEDICAL_ROLE_OPTIONS = [
    MEDICAL_ROLE_PLACEHOLDER,
    "Psikolog",
    "Dokter Spesialis Kedokteran Jiwa",
]

CARE_PAGES = [
    "Home",
    "Audore Assistant",
    "Edukasi",
    "Konsultasi",
    "Komunitas",
]

MEDICAL_PAGES = [
    "Home",
    "Konsultasi",
]

ADMIN_PAGES = [
    "Home",
    "Admin Dashboard",
    "Audore Assistant",
    "Edukasi",
    "Konsultasi",
    "Komunitas",
]

PAGES = CARE_PAGES + ["Admin Dashboard"]

FEATURES = {
    "Admin Dashboard": {
        "description": (
            "Mengelola data pengguna, tenaga medis, konten aplikasi, "
            "dan pengaturan umum sistem Audore."
        ),
        "color": "#F2F4FF",
        "accent": "#7A5AF8",
        "button_type": "secondary",
    },
    "Audore Assistant": {
        "description": (
            "Membantu mengidentifikasi kategori permasalahan caregiver "
            "berdasarkan keluhan yang disampaikan."
        ),
        "color": "#FFDDE7",
        "accent": "#FF7A98",
        "button_type": "secondary",
    },
    "Edukasi": {
        "description": (
            "Menyediakan informasi edukatif untuk mendukung pemahaman "
            "caregiver dalam pendampingan anak."
        ),
        "color": "#FFF0C9",
        "accent": "#F3B43F",
        "button_type": "secondary",
    },
    "Konsultasi": {
        "description": (
            "Membantu caregiver memperoleh arahan awal melalui layanan "
            "konsultasi yang tersedia."
        ),
        "color": "#EAF6FF",
        "accent": "#65A9F5",
        "button_type": "secondary",
    },
    "Komunitas": {
        "description": (
            "Menjadi ruang berbagi informasi dan dukungan antar-caregiver "
            "dalam komunitas Audore."
        ),
        "color": "#E9E1FF",
        "accent": "#8D73E6",
        "button_type": "secondary",
    },
}


def get_pages_for_role(user_type=None):
    """Return pages that can be accessed by a specific role."""
    role = user_type or st.session_state.get("user_type", "")

    if role == "Admin":
        return ADMIN_PAGES

    if role == "Tenaga Medis":
        return MEDICAL_PAGES

    return CARE_PAGES


def get_default_page_for_role(user_type):
    """Return landing page after login based on role."""
    if user_type == "Admin":
        return "Admin Dashboard"

    if user_type == "Tenaga Medis":
        return "Konsultasi"

    return "Home"


# ======================
# Styling
# ======================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"] {
        color-scheme: light;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, #FFF0F4 0%, transparent 30%),
            radial-gradient(circle at top right, #EAF6FF 0%, transparent 32%),
            radial-gradient(circle at bottom right, #EFE8FF 0%, transparent 34%),
            linear-gradient(180deg, #FFF9FA 0%, #F8FBFF 48%, #F4FCFF 100%);
        color: #2F2A38;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    footer {
        display: none !important;
    }

    section[data-testid="stSidebar"] {
        background:
            radial-gradient(circle at top left, #FFF0F4 0%, transparent 42%),
            radial-gradient(circle at bottom right, #EFE8FF 0%, transparent 38%),
            rgba(255, 255, 255, 0.92);
        border-right: 1px solid rgba(122, 90, 248, 0.12);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.1rem;
    }

    .sidebar-brand {
        background:
            radial-gradient(circle at top left, #FFDDE7 0%, transparent 48%),
            radial-gradient(circle at bottom right, #EAF6FF 0%, transparent 45%),
            linear-gradient(145deg, #FFFFFF 0%, #FFF9FA 100%);
        border: 1px solid rgba(122, 90, 248, 0.12);
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 12px 28px rgba(88, 72, 124, 0.08);
    }

    .sidebar-brand h2 {
        color: #111111;
        font-size: 1.4rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0;
    }

    .sidebar-brand p {
        color: #6A6278;
        font-size: 0.84rem;
        line-height: 1.45;
        margin: 0.3rem 0 0 0;
    }

    .sidebar-profile {
        background: rgba(255, 255, 255, 0.78);
        border: 1px solid rgba(122, 90, 248, 0.10);
        border-radius: 16px;
        padding: 0.8rem 0.9rem;
        margin-bottom: 0.75rem;
    }

    .sidebar-profile-label {
        color: #8A819A;
        font-size: 0.76rem;
        margin-bottom: 0.2rem;
    }

    .sidebar-profile-name {
        color: #2F2A38;
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
    }

    .sidebar-profile-role {
        color: #6A6278;
        font-size: 0.84rem;
    }

    .sidebar-menu-title {
        color: #6A6278;
        font-size: 0.82rem;
        font-weight: 800;
        margin: 0.25rem 0 0.25rem 0;
    }

    div[role="radiogroup"] {
        gap: 0.02rem;
    }

    div[role="radiogroup"] label {
        border-radius: 14px;
        padding: 0.16rem 0.3rem;
    }

    div[role="radiogroup"] label:hover {
        background: rgba(255, 221, 231, 0.45);
    }

    .login-shell {
        max-width: 1080px;
        margin: 1.3rem auto 0 auto;
    }

    .login-brand-card {
        min-height: 550px;
        background:
            radial-gradient(circle at top left, #FFDDE7 0%, transparent 40%),
            radial-gradient(circle at center right, #EAF6FF 0%, transparent 38%),
            radial-gradient(circle at bottom right, #E9E1FF 0%, transparent 42%),
            linear-gradient(145deg, #FFFFFF 0%, #F8FBFF 100%);
        border: 1px solid rgba(122, 90, 248, 0.12);
        border-radius: 28px;
        box-shadow: 0 24px 60px rgba(88, 72, 124, 0.14);
        padding: 2.4rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .login-badge {
        display: inline-block;
        width: fit-content;
        background: linear-gradient(90deg, #FFDDE7 0%, #EAF6FF 100%);
        color: #3A2E3F;
        border-radius: 999px;
        padding: 0.45rem 0.85rem;
        font-size: 0.86rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
    }

    .login-brand-card h1 {
        color: #111111;
        font-size: 3rem;
        font-weight: 800;
        margin: 0 0 0.8rem 0;
        letter-spacing: 0;
    }

    .login-brand-card p {
        color: #5F5870;
        font-size: 1.05rem;
        line-height: 1.75;
        margin: 0;
    }

    .login-info-grid {
        display: grid;
        gap: 0.85rem;
        margin-top: 2rem;
    }

    .login-info-item {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(122, 90, 248, 0.10);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        color: #514568;
        font-size: 0.94rem;
        line-height: 1.55;
    }

    div[data-testid="stForm"] {
        border: 0;
        padding: 0;
        box-shadow: none;
        background: transparent;
    }

    .login-form-title h2 {
        color: #111111;
        font-size: 1.75rem;
        font-weight: 800;
        margin: 0 0 0.35rem 0;
        letter-spacing: 0;
    }

    .login-form-title p {
        color: #6A6278;
        margin: 0 0 1.3rem 0;
        line-height: 1.6;
    }

    .auth-note {
        color: #6A6278 !important;
        font-size: 0.9rem;
        line-height: 1.55;
        margin-top: 0.9rem;
        margin-bottom: 0.25rem;
        text-align: center;
    }

    .home-hero {
        background:
            radial-gradient(circle at top left, #FFDDE7 0%, transparent 38%),
            radial-gradient(circle at top right, #EAF6FF 0%, transparent 36%),
            radial-gradient(circle at bottom right, #E9E1FF 0%, transparent 42%),
            linear-gradient(145deg, #FFFFFF 0%, #FFF9FA 100%);
        border: 1px solid rgba(122, 90, 248, 0.10);
        border-radius: 28px;
        box-shadow: 0 18px 42px rgba(88, 72, 124, 0.10);
        padding: 2rem 2.2rem;
        margin-bottom: 1.35rem;
    }

    .home-hero h1 {
        color: #111111;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0 0 0.55rem 0;
        letter-spacing: 0;
    }

    .home-hero p {
        color: #5F5870;
        font-size: 1.02rem;
        line-height: 1.7;
        margin: 0;
    }

    .home-section-header {
        margin: 0.25rem 0 1.1rem 0;
    }

    .home-section-title {
        color: #111111;
        font-size: 1.72rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0;
    }

    .home-section-subtitle {
        color: #6A6278;
        font-size: 0.95rem;
        margin: 0.25rem 0 0 0;
        line-height: 1.55;
    }

    .feature-card-home {
        border: 1px solid rgba(122, 90, 248, 0.12);
        border-radius: 28px;
        box-shadow: 0 18px 42px rgba(88, 72, 124, 0.10);
        padding: 2rem 2.1rem;
        min-height: 15.5rem;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        margin-bottom: 0.9rem;
        transition: 0.2s ease;
    }

    .feature-card-home:hover {
        transform: translateY(-2px);
        box-shadow: 0 22px 50px rgba(88, 72, 124, 0.14);
        border-color: rgba(122, 90, 248, 0.20);
    }

    .feature-card-home.feature-pink {
        background:
            radial-gradient(circle at top left, #FFDDE7 0%, rgba(255, 221, 231, 0) 46%),
            radial-gradient(circle at bottom right, #EAF6FF 0%, rgba(234, 246, 255, 0) 48%),
            linear-gradient(145deg, #FFFFFF 0%, #FFF9FA 100%);
    }

    .feature-card-home.feature-yellow {
        background:
            radial-gradient(circle at top left, #FFF0C9 0%, rgba(255, 240, 201, 0) 46%),
            radial-gradient(circle at bottom right, #E9E1FF 0%, rgba(233, 225, 255, 0) 48%),
            linear-gradient(145deg, #FFFFFF 0%, #FFFCF2 100%);
    }

    .feature-card-home.feature-blue {
        background:
            radial-gradient(circle at top left, #EAF6FF 0%, rgba(234, 246, 255, 0) 46%),
            radial-gradient(circle at bottom right, #E9E1FF 0%, rgba(233, 225, 255, 0) 48%),
            linear-gradient(145deg, #FFFFFF 0%, #F8FBFF 100%);
    }

    .feature-card-home.feature-purple {
        background:
            radial-gradient(circle at top left, #E9E1FF 0%, rgba(233, 225, 255, 0) 46%),
            radial-gradient(circle at bottom right, #FFDDE7 0%, rgba(255, 221, 231, 0) 48%),
            linear-gradient(145deg, #FFFFFF 0%, #FBF8FF 100%);
    }

    .feature-badge {
        display: inline-block;
        width: fit-content;
        border-radius: 999px;
        color: #3A3444;
        font-size: 0.84rem;
        font-weight: 800;
        padding: 0.5rem 0.95rem;
        margin-bottom: 1.55rem;
    }

    .feature-pink .feature-badge {
        background: rgba(255, 221, 231, 0.90);
    }

    .feature-yellow .feature-badge {
        background: rgba(255, 240, 201, 0.95);
    }

    .feature-blue .feature-badge {
        background: rgba(234, 246, 255, 0.95);
    }

    .feature-purple .feature-badge {
        background: rgba(233, 225, 255, 0.95);
    }

    .feature-title {
        color: #2F2A38;
        font-size: 1.7rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0;
        line-height: 1.2;
    }

    .feature-description {
        color: #4F485D;
        font-size: 1rem;
        line-height: 1.72;
        margin: 1rem 0 0 0;
    }

    label,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p {
        color: #2F2A38 !important;
    }

    div[data-testid="stTextInput"] label,
    div[data-testid="stTextInput"] label p,
    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] label p,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSelectbox"] label p {
        color: #2F2A38 !important;
    }

    div[data-testid="stTextInput"] input {
        background: #F1F7FF !important;
        color: #2F2A38 !important;
        border-radius: 14px !important;
        border: 1px solid rgba(122, 90, 248, 0.16) !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #8A819A !important;
    }

    div[data-testid="stButton"] > button,
    div[data-testid="stFormSubmitButton"] > button {
        border-radius: 999px;
        font-weight: 700;
        min-height: 2.55rem;
        background: rgba(255, 255, 255, 0.92) !important;
        color: #514568 !important;
        border: 1px solid rgba(122, 90, 248, 0.18) !important;
        box-shadow: 0 10px 22px rgba(122, 90, 248, 0.12);
    }

    div[data-testid="stVerticalBlock"]:has(.feature-card-home) div[data-testid="stButton"] > button {
        min-height: 2.65rem;
        font-size: 0.98rem;
        border-radius: 999px !important;
        background:
            radial-gradient(circle at top left, rgba(255, 221, 231, 0.55) 0%, transparent 48%),
            radial-gradient(circle at bottom right, rgba(234, 246, 255, 0.62) 0%, transparent 48%),
            rgba(255, 255, 255, 0.90) !important;
        border: 1px solid rgba(122, 90, 248, 0.14) !important;
        box-shadow: 0 10px 22px rgba(88, 72, 124, 0.07) !important;
        color: #3A3444 !important;
    }

    div[data-testid="stButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: #F8FBFF !important;
        color: #2F2A38 !important;
        border-color: rgba(122, 90, 248, 0.28) !important;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .login-shell {
            margin-top: 0.6rem;
        }

        .login-brand-card {
            min-height: auto;
            padding: 1.6rem;
        }

        .login-brand-card h1 {
            font-size: 2.2rem;
        }

        .home-hero {
            padding: 1.6rem;
        }

        .home-hero h1 {
            font-size: 1.85rem;
        }

        .home-section-header {
            display: block;
        }

        .feature-panel {
            min-height: auto;
            padding: 1.35rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ======================
# Navigation Helpers
# ======================
def initialize_page_state():
    """Prepare authentication and active page values."""
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    if "active_page" not in st.session_state:
        st.session_state.active_page = "Home"

    if "user_name" not in st.session_state:
        st.session_state.user_name = ""

    if "user_type" not in st.session_state:
        st.session_state.user_type = ""

    if "medical_role" not in st.session_state:
        st.session_state.medical_role = ""

    if "registered_users" not in st.session_state:
        st.session_state.registered_users = {}

    available_pages = get_pages_for_role(st.session_state.user_type)

    if st.session_state.active_page not in available_pages:
        st.session_state.active_page = get_default_page_for_role(
            st.session_state.user_type
        )


def authenticate_user(name, password, login_user_type):
    """Validate login using SQLite database."""
    if not name.strip() or not password.strip():
        return False, "Nama dan password harus diisi."

    is_valid, account = db_login_user(
        nama=name,
        password=password,
        role=login_user_type,
    )

    if not is_valid or not account:
        return False, (
            "Akun belum terdaftar, password tidak sesuai, atau jenis akun "
            "yang dipilih tidak sesuai. Silakan periksa kembali data login."
        )

    return True, account


def register_account(name, password, confirm_password, user_type, medical_role):
    """Register new user account into SQLite database."""
    if not name.strip() or not password.strip() or not confirm_password.strip():
        return False, "Nama, password, dan konfirmasi password harus diisi."

    if password != confirm_password:
        return False, "Konfirmasi password tidak sesuai."

    if user_type not in USER_TYPES:
        return False, "Jenis akun tidak valid."

    if user_type == "Tenaga Medis" and not medical_role:
        return False, "Jenis tenaga medis harus dipilih."

    is_registered, message = db_register_user(
        nama=name,
        password=password,
        role=user_type,
        medical_role=medical_role if user_type == "Tenaga Medis" else "",
    )

    return is_registered, message


def go_to_page(page_name):
    """Move to the selected page and refresh the interface."""
    st.session_state.active_page = page_name
    st.rerun()


# ======================
# Authentication Page
# ======================
def render_login():
    """Render login and registration page before entering Audore."""
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        .block-container {
            max-width: 1120px;
            padding-top: 1.2rem;
        }

        div[data-testid="stForm"] {
            min-height: 550px;
            background:
                radial-gradient(circle at top right, rgba(234, 246, 255, 0.65) 0%, transparent 42%),
                rgba(255, 255, 255, 0.94) !important;
            border: 1px solid rgba(122, 90, 248, 0.12) !important;
            border-radius: 28px !important;
            box-shadow: 0 24px 60px rgba(88, 72, 124, 0.10) !important;
            padding: 2.1rem !important;
        }

        div[data-testid="stForm"] > div {
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="login-shell">', unsafe_allow_html=True)

    left_col, right_col = st.columns([1.05, 0.95], gap="large")

    with left_col:
        st.markdown(
            """
            <div class="login-brand-card">
                <div class="login-badge">Audore Assistant</div>
                <h1>Audore</h1>
                <p>
                    Pendamping digital bagi caregiver anak dengan Autism
                    Spectrum Disorder.
                </p>
                <div class="login-info-grid">
                    <div class="login-info-item">
                        Akses caregiver untuk menggunakan fitur pendampingan,
                        edukasi, komunitas, dan penjadwalan konsultasi.
                    </div>
                    <div class="login-info-item">
                        Akses tenaga medis untuk melihat dan menindaklanjuti
                        daftar konsultasi sesuai peran profesional.
                    </div>
                    <div class="login-info-item">
                        Akses admin untuk mengelola akun pengguna, tenaga medis,
                        konten aplikasi, dan struktur fitur utama.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        if st.session_state.auth_mode == "login":
            with st.form("login_form"):
                st.markdown(
                    """
                    <div class="login-form-title">
                        <h2>Masuk Akun</h2>
                        <p>Masukkan nama, password, dan jenis akun yang sudah terdaftar.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                name = st.text_input("Nama", key="login_name")

                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                )

                login_user_type = st.radio(
                    "Masuk sebagai",
                    USER_TYPES,
                    horizontal=True,
                    key="login_user_type",
                )

                submitted = st.form_submit_button(
                    "Masuk",
                    use_container_width=True,
                )

                st.markdown(
                    """
                    <div class="auth-note">
                        Belum punya akun?
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                switch_to_register = st.form_submit_button(
                    "Daftar",
                    use_container_width=True,
                )

            if switch_to_register:
                st.session_state.auth_mode = "register"
                st.rerun()

            if submitted:
                is_valid, result = authenticate_user(
                    name,
                    password,
                    login_user_type,
                )

                if is_valid:
                    account = result

                    st.session_state.is_authenticated = True
                    st.session_state.user_id = account.get("id_user")
                    st.session_state.user_name = account["nama"]
                    st.session_state.user_type = account["role"]
                    st.session_state.medical_role = (
                        account.get("medical_role", "")
                        if account["role"] == "Tenaga Medis"
                        else ""
                    )

                    st.session_state.active_page = get_default_page_for_role(
                        account["role"]
                    )

                    if account["role"] == "Tenaga Medis":
                        st.session_state.halaman_konsultasi = "home"

                    st.rerun()
                else:
                    st.error(result)

        else:
            with st.form("register_form"):
                st.markdown(
                    """
                    <div class="login-form-title">
                        <h2>Daftar Akun</h2>
                        <p>Buat akun baru untuk menggunakan fitur Audore.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                register_name = st.text_input("Nama", key="register_name")

                register_password = st.text_input(
                    "Password",
                    type="password",
                    key="register_password",
                )

                confirm_password = st.text_input(
                    "Konfirmasi Password",
                    type="password",
                    key="confirm_password",
                )

                register_user_type = st.radio(
                    "Daftar sebagai",
                    USER_TYPES,
                    horizontal=True,
                    key="register_user_type",
                )

                register_medical_role = ""
                if register_user_type == "Tenaga Medis":
                    selected_medical_role = st.selectbox(
                        "Jenis Tenaga Medis",
                        MEDICAL_ROLE_OPTIONS,
                        key="register_medical_role",
                    )
                    register_medical_role = (
                        ""
                        if selected_medical_role == MEDICAL_ROLE_PLACEHOLDER
                        else selected_medical_role
                    )

                registered = st.form_submit_button(
                    "Daftar dan Masuk",
                    use_container_width=True,
                )

                st.markdown(
                    """
                    <div class="auth-note">
                        Sudah punya akun?
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                switch_to_login = st.form_submit_button(
                    "Masuk",
                    use_container_width=True,
                )

            if switch_to_login:
                st.session_state.auth_mode = "login"
                st.rerun()

            if registered:
                is_registered, message = register_account(
                    register_name,
                    register_password,
                    confirm_password,
                    register_user_type,
                    register_medical_role,
                )

                if is_registered:
                    login_success, account = db_login_user(
                        nama=register_name,
                        password=register_password,
                        role=register_user_type,
                    )

                    st.session_state.is_authenticated = True
                    st.session_state.user_id = (
                        account.get("id_user") if login_success and account else None
                    )
                    st.session_state.user_name = register_name.strip()
                    st.session_state.user_type = register_user_type
                    st.session_state.medical_role = register_medical_role

                    st.session_state.active_page = get_default_page_for_role(
                        register_user_type
                    )

                    if register_user_type == "Tenaga Medis":
                        st.session_state.halaman_konsultasi = "home"

                    st.success("Akun berhasil dibuat.")
                    st.rerun()
                else:
                    st.error(message)

    st.markdown("</div>", unsafe_allow_html=True)


# ======================
# Sidebar
# ======================
def render_sidebar():
    """Render compact and styled sidebar navigation."""
    if st.session_state.user_type == "Tenaga Medis":
        role_label = st.session_state.medical_role or "Tenaga Medis"
    elif st.session_state.user_type == "Admin":
        role_label = "Admin"
    else:
        role_label = "Caregiver"

    safe_user_name = html.escape(st.session_state.user_name)
    safe_role_label = html.escape(role_label)

    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <h2>Audore</h2>
            <p>Pendamping digital bagi caregiver anak dengan Autism Spectrum Disorder.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        f"""
        <div class="sidebar-profile">
            <div class="sidebar-profile-label">Profil pengguna</div>
            <div class="sidebar-profile-name">{safe_user_name}</div>
            <div class="sidebar-profile-role">{safe_role_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        '<div class="sidebar-menu-title">Menu</div>',
        unsafe_allow_html=True,
    )

    available_pages = get_pages_for_role()

    if st.session_state.active_page not in available_pages:
        st.session_state.active_page = get_default_page_for_role(
            st.session_state.user_type
        )

    selected_page = st.sidebar.radio(
        "Menu",
        available_pages,
        index=available_pages.index(st.session_state.active_page),
        label_visibility="collapsed",
    )

    if selected_page != st.session_state.active_page:
        st.session_state.active_page = selected_page
        st.rerun()

    if st.sidebar.button("Keluar", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.active_page = "Home"
        st.session_state.user_id = None
        st.session_state.user_name = ""
        st.session_state.user_type = ""
        st.session_state.medical_role = ""
        st.session_state.auth_mode = "login"
        st.rerun()


# ======================
# Page Components
# ======================
def render_feature_card(page_name):
    """Render one feature card with the button inside the same visual container."""
    feature = FEATURES[page_name]
    feature_meta = {
        "Admin Dashboard": ("feature-purple", "Admin"),
        "Audore Assistant": ("feature-pink", "Identifikasi"),
        "Edukasi": ("feature-yellow", "Edukasi ASD"),
        "Konsultasi": ("feature-blue", "Konsultasi"),
        "Komunitas": ("feature-purple", "Komunitas"),
    }[page_name]
    feature_style, feature_badge = feature_meta

    with st.container():
        st.markdown(
            f"""
            <div
                class="feature-card-home {feature_style}"
                style="--feature-color: {feature['color']}; --feature-accent: {feature['accent']};"
            >
                <div class="feature-badge">{feature_badge}</div>
                <div class="feature-title">{page_name}</div>
                <p class="feature-description">{feature['description']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Buka",
            key=f"open_{page_name}",
            type=feature["button_type"],
            use_container_width=True,
        ):
            go_to_page(page_name)


def render_home():
    """Render Audore home page."""
    user_name = html.escape(st.session_state.user_name or "Pengguna")

    if st.session_state.user_type == "Admin":
        hero_text = (
            "Kelola data pengguna, akses tenaga medis, konten aplikasi, "
            "serta pantau struktur fitur utama Audore."
        )
    elif st.session_state.user_type == "Tenaga Medis":
        hero_text = (
            "Pantau dan tindak lanjuti layanan konsultasi sesuai peran "
            "profesional pada aplikasi Audore."
        )
    else:
        hero_text = (
            "Pilih fitur yang ingin digunakan untuk mendukung pendampingan, "
            "edukasi, konsultasi, dan komunikasi dalam komunitas Audore."
        )

    st.markdown(
        f"""
        <div class="home-hero">
            <div class="login-badge">Audore Assistant</div>
            <h1>Selamat Datang, {user_name}</h1>
            <p>{hero_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="home-section-header">
            <h2 class="home-section-title">Akses Fitur</h2>
            <p class="home-section-subtitle">
                Fitur yang tampil disesuaikan dengan jenis akun dan hak akses pengguna.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pages_to_show = [
        page
        for page in get_pages_for_role()
        if page != "Home" and page in FEATURES
    ]

    for index in range(0, len(pages_to_show), 2):
        columns = st.columns(2, gap="large")

        for column, page_name in zip(columns, pages_to_show[index:index + 2]):
            with column:
                render_feature_card(page_name)

        st.write("")


def render_admin_dashboard():
    """Render admin dashboard and account-management controls."""
    st.markdown(
        """
        <div class="home-hero">
            <div class="login-badge">Admin</div>
            <h1>Admin Dashboard</h1>
            <p>
                Halaman ini digunakan admin untuk memantau akun pengguna,
                tenaga medis, dan struktur fitur utama pada aplikasi Audore.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    notice = st.session_state.pop("admin_account_notice", None)
    if notice:
        notice_type, notice_message = notice
        if notice_type == "success":
            st.success(notice_message)
        else:
            st.error(notice_message)

    registered_users = get_all_users()

    total_users = len(registered_users)
    total_caregiver = sum(
        1 for user in registered_users
        if user.get("role") == "Caregiver"
    )
    total_medical = sum(
        1 for user in registered_users
        if user.get("role") == "Tenaga Medis"
    )
    total_admin = sum(
        1 for user in registered_users
        if user.get("role") == "Admin"
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Akun", total_users)
    col2.metric("Caregiver", total_caregiver)
    col3.metric("Tenaga Medis", total_medical)
    col4.metric("Admin", total_admin)

    st.markdown("### Data Akun Terdaftar")

    if not registered_users:
        st.info("Belum ada akun yang terdaftar pada database.")
        return

    account_rows = []

    for account in registered_users:
        account_rows.append(
            {
                "Nama": account.get("nama", "-"),
                "Jenis Akun": account.get("role", "-"),
                "Peran Medis": (
                    account.get("medical_role") or "-"
                    if account.get("role") == "Tenaga Medis"
                    else "-"
                ),
                "Tanggal Daftar": account.get("created_at", "-"),
            }
        )

    st.dataframe(account_rows, use_container_width=True, hide_index=True)

    st.markdown("### Kelola Akun")
    st.caption(
        "Pilih akun yang ingin dihapus. Akun admin yang sedang digunakan "
        "tidak dapat dihapus dari sesi ini."
    )

    current_user_id = st.session_state.get("user_id")
    deletable_users = [
        user
        for user in registered_users
        if user.get("id_user") != current_user_id
    ]

    if not deletable_users:
        st.info("Tidak ada akun lain yang dapat dihapus.")
        return

    user_by_id = {
        int(user["id_user"]): user
        for user in deletable_users
        if user.get("id_user") is not None
    }

    # Gunakan form agar pilihan akun, konfirmasi, dan tombol dikirim dalam
    # satu proses. Key versi baru juga mencegah nilai widget lama tersimpan
    # setelah file audore.db diganti saat aplikasi masih berjalan.
    with st.form("admin_delete_account_form_v2", clear_on_submit=True):
        selected_user_id = st.selectbox(
            "Pilih akun",
            options=list(user_by_id.keys()),
            format_func=lambda user_id: (
                f'{user_by_id[user_id].get("nama", "-")} — '
                f'{user_by_id[user_id].get("role", "-")}'
                + (
                    f' ({user_by_id[user_id].get("medical_role")})'
                    if user_by_id[user_id].get("medical_role")
                    else ""
                )
            ),
            key="admin_delete_user_id_v2",
        )

        selected_account = user_by_id.get(selected_user_id)
        if selected_account:
            st.warning(
                "Akun yang dipilih: "
                f'**{selected_account.get("nama", "-")}** '
                f'({selected_account.get("role", "-")}). '
                "Tindakan ini tidak dapat dibatalkan."
            )

        confirm_delete = st.checkbox(
            "Saya yakin ingin menghapus akun tersebut.",
            key="admin_confirm_delete_user_v2",
        )

        delete_submitted = st.form_submit_button(
            "Hapus Akun",
            type="primary",
            use_container_width=True,
        )

    if delete_submitted:
        # Validasi ulang terhadap data terbaru untuk mencegah akun yang salah
        # terhapus akibat session_state lama atau database yang baru diganti.
        latest_users = {
            int(user["id_user"]): user
            for user in get_all_users()
            if user.get("id_user") is not None
        }
        latest_account = latest_users.get(int(selected_user_id))

        if not confirm_delete:
            st.warning("Centang kotak konfirmasi sebelum menghapus akun.")
        elif int(selected_user_id) == int(current_user_id or -1):
            st.error("Akun admin yang sedang digunakan tidak dapat dihapus.")
        elif latest_account is None:
            st.error("Akun tidak ditemukan. Muat ulang halaman lalu pilih kembali akun.")
        else:
            deleted, message = db_delete_user(int(selected_user_id))
            st.session_state.admin_account_notice = (
                "success" if deleted else "error",
                message,
            )
            st.rerun()


# ======================
# Main Application
# ======================
def main():
    initialize_page_state()

    if not st.session_state.is_authenticated:
        render_login()
        return

    render_sidebar()

    active_page = st.session_state.active_page

    if active_page == "Home":
        render_home()
    elif active_page == "Admin Dashboard":
        render_admin_dashboard()
    elif active_page == "Audore Assistant":
        run_ml_app()
    elif active_page == "Edukasi":
        run_edukasi()
    elif active_page == "Konsultasi":
        run_konsultasi()
    elif active_page == "Komunitas":
        run_komunitas()


if __name__ == "__main__":
    main()
