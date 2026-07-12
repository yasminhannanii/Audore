import html
from textwrap import dedent

import streamlit as st


def markdown_html(content):
    st.markdown(dedent(content).strip(), unsafe_allow_html=True)


def run_edukasi():
    markdown_html(
        """
        <style>
        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"] {
            color-scheme: light;
        }

        .education-page {
            max-width: 1040px;
            margin: 0 auto;
        }

        .back-button-space {
            margin-bottom: 0.9rem;
        }

        .education-hero {
            background:
                radial-gradient(circle at top left, #FFF0C9 0%, transparent 38%),
                radial-gradient(circle at bottom right, #E9E1FF 0%, transparent 42%),
                linear-gradient(145deg, #FFFFFF 0%, #FFF9FA 100%);
            border: 1px solid rgba(122, 90, 248, 0.10);
            border-radius: 28px;
            box-shadow: 0 18px 42px rgba(88, 72, 124, 0.10);
            padding: 2.2rem 2.4rem;
            margin-bottom: 1.4rem;
        }

        .education-badge {
            display: inline-block;
            background: #FFF0C9;
            color: #3A2E3F;
            border-radius: 999px;
            padding: 0.45rem 0.85rem;
            font-size: 0.86rem;
            font-weight: 700;
            margin-bottom: 1.1rem;
        }

        .education-hero h1 {
            color: #111111;
            font-size: 2.25rem;
            font-weight: 800;
            margin: 0 0 0.65rem 0;
            letter-spacing: 0;
        }

        .education-hero p {
            color: #5F5870;
            font-size: 1.05rem;
            line-height: 1.7;
            margin: 0;
        }

        .education-info-card {
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid rgba(122, 90, 248, 0.10);
            border-radius: 22px;
            padding: 1.1rem 1.25rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 14px 34px rgba(88, 72, 124, 0.08);
        }

        .education-info-card h3 {
            color: #2F2A38;
            font-size: 1.05rem;
            font-weight: 800;
            margin: 0 0 0.35rem 0;
        }

        .education-info-card p {
            color: #5F5870;
            font-size: 0.95rem;
            line-height: 1.6;
            margin: 0;
        }

        .section-title {
            color: #111111;
            font-size: 1.55rem;
            font-weight: 800;
            margin: 0.4rem 0 0.45rem 0;
        }

        .section-subtitle {
            color: #6A6278;
            font-size: 0.96rem;
            line-height: 1.6;
            margin: 0 0 1.2rem 0;
        }

        div[data-testid="stTabs"] button {
            font-weight: 700;
            color: #514568;
        }

        div[data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.86) !important;
            border: 1px solid rgba(122, 90, 248, 0.10) !important;
            border-radius: 18px !important;
            box-shadow: 0 10px 24px rgba(88, 72, 124, 0.06) !important;
            margin-bottom: 0.75rem !important;
        }

        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] summary p {
            font-weight: 800 !important;
            color: #2F2A38 !important;
        }

        .school-card {
            position: relative;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(122, 90, 248, 0.10);
            border-radius: 22px;
            box-shadow: 0 18px 38px rgba(88, 72, 124, 0.10);
            padding: 1.35rem;
            min-height: 17.4rem;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            margin-bottom: 0.75rem;
        }

        .school-card::before {
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 5rem;
            background:
                radial-gradient(circle at top left, rgba(255, 221, 231, 0.92) 0%, transparent 50%),
                linear-gradient(135deg, #FFDDE7 0%, rgba(255, 255, 255, 0.50) 100%);
        }

        .school-tone-1::before {
            background:
                radial-gradient(circle at top left, rgba(180, 106, 114, 0.92) 0%, transparent 50%),
                linear-gradient(135deg, #B46A72 0%, rgba(255, 255, 255, 0.56) 100%);
        }

        .school-tone-2::before {
            background:
                radial-gradient(circle at top left, rgba(171, 181, 138, 0.92) 0%, transparent 50%),
                linear-gradient(135deg, #ABB58A 0%, rgba(255, 255, 255, 0.56) 100%);
        }

        .school-tone-3::before {
            background:
                radial-gradient(circle at top left, rgba(169, 183, 198, 0.92) 0%, transparent 50%),
                linear-gradient(135deg, #A9B7C6 0%, rgba(255, 255, 255, 0.56) 100%);
        }

        .school-tone-4::before {
            background:
                radial-gradient(circle at top left, rgba(45, 58, 71, 0.92) 0%, transparent 50%),
                linear-gradient(135deg, #2D3A47 0%, rgba(255, 255, 255, 0.56) 100%);
        }

        .school-card > * {
            position: relative;
            z-index: 1;
        }

        .school-card-top {
            display: flex;
            gap: 0.9rem;
            align-items: flex-start;
            margin-bottom: 1.45rem;
        }

        .school-number {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 2.65rem;
            height: 2.65rem;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.74);
            border: 1px solid rgba(255, 255, 255, 0.82);
            color: #5F5568;
            font-size: 0.82rem;
            font-weight: 800;
        }

        .school-tag {
            display: inline-block;
            background: rgba(255, 255, 255, 0.66);
            border: 1px solid rgba(255, 255, 255, 0.78);
            border-radius: 999px;
            color: #5F5568;
            font-size: 0.76rem;
            font-weight: 700;
            padding: 0.3rem 0.68rem;
        }

        .school-accent {
            width: 2.7rem;
            height: 0.28rem;
            border-radius: 999px;
            background: #FF7194;
            margin: 0 0 0.82rem 0;
        }

        .school-tone-1 .school-accent {
            background: #B46A72;
        }

        .school-tone-2 .school-accent {
            background: #ABB58A;
        }

        .school-tone-3 .school-accent {
            background: #A9B7C6;
        }

        .school-tone-4 .school-accent {
            background: #2D3A47;
        }

        .school-card h3 {
            color: #2F2A38;
            font-size: 1.28rem;
            font-weight: 800;
            margin: 0 0 0.65rem 0;
            letter-spacing: 0;
            line-height: 1.25;
        }

        .school-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin: 0 0 0.95rem 0;
        }

        .school-chip-row span {
            background: rgba(255, 255, 255, 0.68);
            border: 1px solid rgba(122, 90, 248, 0.08);
            border-radius: 999px;
            color: #6A6278;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 0.38rem 0.7rem;
        }

        .school-label {
            color: #6A6278;
            font-size: 0.8rem;
            font-weight: 800;
            margin-bottom: 0.22rem;
        }

        .school-text {
            color: #2F2A38;
            font-size: 1rem;
            line-height: 1.55;
            margin: 0 0 0.95rem 0;
        }

        .school-desc {
            color: #5F5870;
            font-size: 0.94rem;
            line-height: 1.6;
            margin: 0;
        }

        .school-empty-card {
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid rgba(122, 90, 248, 0.10);
            border-radius: 22px;
            padding: 1.2rem;
            color: #5F5870;
            box-shadow: 0 12px 28px rgba(88, 72, 124, 0.06);
        }

        .detail-card {
            background:
                radial-gradient(circle at top left, #FFF0C9 0%, transparent 42%),
                radial-gradient(circle at bottom right, #E9E1FF 0%, transparent 40%),
                rgba(255, 255, 255, 0.92);
            border: 1px solid rgba(122, 90, 248, 0.12);
            border-radius: 28px;
            box-shadow: 0 18px 42px rgba(88, 72, 124, 0.10);
            padding: 2rem;
            margin-bottom: 1.2rem;
        }

        .detail-card h1 {
            color: #111111;
            font-size: 2rem;
            font-weight: 800;
            margin: 0 0 0.9rem 0;
        }

        .detail-desc {
            color: #5F5870;
            line-height: 1.65;
            margin: 0;
            font-size: 1rem;
        }

        .detail-meta {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.85rem;
            margin-top: 1rem;
        }

        .detail-meta-item {
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(122, 90, 248, 0.10);
            border-radius: 16px;
            padding: 0.9rem 1rem;
        }

        .detail-meta-label {
            color: #8A819A;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .detail-meta-value {
            color: #2F2A38;
            font-size: 0.95rem;
            line-height: 1.5;
            font-weight: 700;
        }

        .content-card {
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid rgba(122, 90, 248, 0.10);
            border-radius: 22px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 12px 28px rgba(88, 72, 124, 0.06);
        }

        .content-card h3 {
            color: #2F2A38;
            font-size: 1.08rem;
            font-weight: 800;
            margin: 0 0 0.6rem 0;
        }

        .content-card p,
        .content-card li {
            color: #5F5870;
            font-size: 0.95rem;
            line-height: 1.65;
        }

        label,
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] p,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p {
            color: #2F2A38 !important;
        }

        div[data-testid="stTextInput"] input {
            border-radius: 16px !important;
            border: 1px solid rgba(122, 90, 248, 0.16) !important;
            background: rgba(255, 255, 255, 0.94) !important;
            color: #2F2A38 !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: #8A819A !important;
            opacity: 1 !important;
        }

        div[data-testid="stButton"] > button,
        div[data-testid="stLinkButton"] > a {
            border-radius: 999px !important;
            font-weight: 700 !important;
            min-height: 2.55rem !important;
            background: rgba(255, 255, 255, 0.92) !important;
            color: #514568 !important;
            border: 1px solid rgba(122, 90, 248, 0.18) !important;
            box-shadow: 0 10px 22px rgba(122, 90, 248, 0.12) !important;
        }

        div[data-testid="stButton"] > button:hover,
        div[data-testid="stLinkButton"] > a:hover {
            background: #F8FBFF !important;
            color: #2F2A38 !important;
            border-color: rgba(122, 90, 248, 0.28) !important;
        }

        @media (max-width: 768px) {
            .education-hero {
                padding: 1.5rem;
            }

            .education-hero h1 {
                font-size: 1.85rem;
            }

            .school-card {
                min-height: auto;
            }

            .detail-meta {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """
    )

    markdown_html('<div class="education-page">')

    markdown_html('<div class="back-button-space">')
    if st.button("Kembali ke Home", use_container_width=False):
        st.session_state.active_page = "Home"
        st.rerun()
    markdown_html("</div>")

    markdown_html(
        """
        <div class="education-hero">
            <div class="education-badge">Edukasi ASD</div>
            <h1>Edukasi Autism Spectrum Disorder</h1>
            <p>
                Pelajari informasi dasar mengenai Autism Spectrum Disorder,
                strategi pendampingan anak, kesehatan mental caregiver, serta
                rekomendasi sekolah inklusi.
            </p>
        </div>
        """
    )

    markdown_html(
        """
        <div class="education-info-card">
            <h3>Pusat informasi caregiver</h3>
            <p>
                Fitur edukasi membantu caregiver memahami kebutuhan anak dengan ASD
                melalui materi ringkas, terarah, dan mudah dipahami.
            </p>
        </div>
        """
    )

    tab1, tab2 = st.tabs(["Materi Edukasi", "Sekolah Inklusi"])

    with tab1:
        markdown_html(
            """
            <h2 class="section-title">Materi Edukasi</h2>
            <p class="section-subtitle">
                Materi dasar untuk membantu caregiver memahami ASD dan strategi
                pendampingan anak sehari-hari.
            </p>
            """
        )

        with st.expander("Apa itu Autism Spectrum Disorder (ASD)?"):
            st.markdown(
                """
                Autism Spectrum Disorder (ASD) merupakan gangguan perkembangan
                neurologis yang memengaruhi kemampuan komunikasi, interaksi sosial,
                serta pola perilaku seseorang.

                Setiap individu dengan ASD memiliki karakteristik yang berbeda
                sehingga disebut sebagai *spectrum disorder*. Gejala umumnya mulai
                terlihat pada masa kanak-kanak dan dapat memengaruhi aktivitas
                sehari-hari.
                """
            )

        with st.expander("Karakteristik dan Gejala ASD"):
            st.markdown(
                """
                **Beberapa karakteristik yang umum ditemukan pada anak ASD antara lain:**

                - Kesulitan berkomunikasi dan berinteraksi sosial.
                - Kontak mata yang terbatas.
                - Perilaku repetitif atau berulang.
                - Memiliki minat yang sangat spesifik pada suatu hal.
                - Sensitif terhadap suara, cahaya, atau sentuhan tertentu.
                """
            )

        with st.expander("Terapi dan Intervensi untuk Anak ASD"):
            st.markdown(
                """
                **Jenis terapi yang umum diberikan kepada anak ASD:**

                - Terapi wicara.
                - Terapi okupasi.
                - Applied Behavior Analysis (ABA).
                - Terapi sensori integrasi.
                - Intervensi pendidikan khusus.

                Pemilihan terapi perlu disesuaikan dengan kebutuhan dan kondisi
                masing-masing anak.
                """
            )

        with st.expander("Cara Mengelola Tantrum pada Anak ASD"):
            st.markdown(
                """
                Tantrum dapat terjadi ketika anak kesulitan menyampaikan kebutuhan
                atau merasa tidak nyaman terhadap lingkungan sekitarnya.

                **Cara yang dapat dilakukan:**

                - Tetap tenang dan tidak memarahi anak.
                - Identifikasi pemicu tantrum.
                - Gunakan instruksi yang sederhana dan jelas.
                - Berikan lingkungan yang aman dan nyaman.
                - Terapkan rutinitas yang konsisten.
                """
            )

        with st.expander("Melatih Kemandirian Anak ASD"):
            st.markdown(
                """
                Kemandirian dapat dilatih secara bertahap melalui aktivitas
                sehari-hari.

                **Contoh kegiatan yang dapat dilatih:**

                - Merapikan mainan sendiri.
                - Menggunakan pakaian secara mandiri.
                - Menyiapkan perlengkapan sekolah.
                - Mengikuti jadwal harian sederhana.

                Berikan pujian atas setiap kemajuan yang berhasil dicapai anak.
                """
            )

        with st.expander("Menjaga Kesehatan Mental Caregiver"):
            st.markdown(
                """
                Menjadi caregiver anak ASD dapat memberikan tantangan fisik maupun
                emosional.

                **Beberapa hal yang dapat dilakukan untuk menjaga kesehatan mental:**

                - Luangkan waktu untuk diri sendiri.
                - Berbagi pengalaman dengan caregiver lain.
                - Mencari dukungan dari keluarga dan lingkungan sekitar.
                - Berkonsultasi dengan tenaga profesional apabila diperlukan.
                """
            )

    with tab2:
        if "halaman_sekolah" not in st.session_state:
            st.session_state.halaman_sekolah = "home"

        if "sekolah_pilih" not in st.session_state:
            st.session_state.sekolah_pilih = None

        sekolah = [
            {
                "nama": "SDN Ketintang II",
                "jenjang": "Sekolah Dasar",
                "alamat": "Jl. Ketintang No.156, Surabaya",
                "deskripsi": (
                    "Menyediakan layanan pendidikan inklusi dengan pendampingan "
                    "guru sesuai kebutuhan siswa."
                ),
                "maps": "https://www.google.com/maps/search/?api=1&query=SDN+Ketintang+II+410+Surabaya",
                "wa": "https://wa.me/628123456789",
                "warna": "#FFDDE7",
                "warna_lembut": "#EAF6FF",
                "aksen": "#FF6E91",
            },
            {
                "nama": "SDN Asemrowo II",
                "jenjang": "Sekolah Dasar",
                "alamat": "Jl. Asemrowo, Surabaya",
                "deskripsi": (
                    "Menyediakan layanan pendidikan inklusi dengan pendampingan "
                    "guru sesuai kebutuhan siswa."
                ),
                "maps": "https://www.google.com/maps/search/?api=1&query=SDN+Asemrowo+II+Surabaya",
                "wa": "https://wa.me/628123456789",
                "warna": "#FFF0C9",
                "warna_lembut": "#FFF9EA",
                "aksen": "#F3B43F",
            },
            {
                "nama": "Sekolah Galuh Handayani",
                "jenjang": "SD, SMP, SMA",
                "alamat": "Jl. Manyar Sambongan No.83-89, Kertajaya, Gubeng, Surabaya",
                "deskripsi": (
                    "Menyediakan layanan pendidikan inklusi dengan pendampingan "
                    "guru sesuai kebutuhan siswa."
                ),
                "maps": "https://www.google.com/maps/search/?api=1&query=Sekolah+Galuh+Handayani+Surabaya",
                "wa": "https://wa.me/628123456789",
                "warna": "#E9E1FF",
                "warna_lembut": "#F8F5FF",
                "aksen": "#8D73E6",
            },
            {
                "nama": "Sekolah Cikal Surabaya",
                "jenjang": "Preschool, TK, SD",
                "alamat": "Jl. Raya Lontar No.103, Sambikerep, Surabaya",
                "deskripsi": (
                    "Menyediakan layanan pendidikan inklusi dengan pendampingan "
                    "guru sesuai kebutuhan siswa."
                ),
                "maps": "https://www.google.com/maps/search/?api=1&query=Sekolah+Cikal+Surabaya",
                "wa": "",
                "warna": "#DDF8EA",
                "warna_lembut": "#F3FFF8",
                "aksen": "#4CC88A",
            },
        ]

        if st.session_state.halaman_sekolah == "home":
            markdown_html(
                """
                <h2 class="section-title">Rekomendasi Sekolah Inklusi</h2>
                <p class="section-subtitle">
                    Cari dan lihat informasi awal sekolah inklusi yang dapat menjadi
                    referensi bagi caregiver.
                </p>
                """
            )

            keyword = st.text_input(
                "Cari sekolah",
                placeholder="Masukkan nama sekolah...",
            )

            filtered_schools = [
                item for item in sekolah
                if keyword.lower() in item["nama"].lower()
            ]

            if not filtered_schools:
                markdown_html(
                    """
                    <div class="school-empty-card">
                        Sekolah tidak ditemukan. Coba gunakan kata kunci lain.
                    </div>
                    """
                )

            col1, col2 = st.columns(2, gap="large")

            for i, item in enumerate(filtered_schools):
                target_col = col1 if i % 2 == 0 else col2

                with target_col:
                    safe_name = html.escape(item["nama"])
                    safe_level = html.escape(item["jenjang"])
                    safe_address = html.escape(item["alamat"])
                    safe_desc = html.escape(item["deskripsi"])

                    st.markdown(
                        (
                            f"<div class='school-card school-tone-{(i % 4) + 1}'>"
                            f"<div class='school-card-top'>"
                            f"<div class='school-number'>{i + 1:02d}</div>"
                            f"<div><div class='school-tag'>Sekolah inklusi</div></div>"
                            f"</div>"
                            f"<div class='school-accent'></div>"
                            f"<h3>{safe_name}</h3>"
                            f"<div class='school-chip-row'>"
                            f"<span>{safe_level}</span>"
                            f"<span>{safe_address}</span>"
                            f"</div>"
                            f"<p class='school-desc'>{safe_desc}</p>"
                            f"</div>"
                        ),
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "Lihat Detail",
                        key=f"detail_{item['nama']}",
                        use_container_width=True,
                    ):
                        st.session_state.sekolah_pilih = item
                        st.session_state.halaman_sekolah = "detail"
                        st.rerun()

        elif st.session_state.halaman_sekolah == "detail":
            sekolah_detail = st.session_state.sekolah_pilih

            if sekolah_detail is None:
                st.session_state.halaman_sekolah = "home"
                st.rerun()

            if st.button("Kembali ke Daftar Sekolah", use_container_width=False):
                st.session_state.halaman_sekolah = "home"
                st.rerun()

            safe_name = html.escape(sekolah_detail["nama"])
            safe_desc = html.escape(sekolah_detail["deskripsi"])
            safe_level = html.escape(sekolah_detail["jenjang"])
            safe_address = html.escape(sekolah_detail["alamat"])

            st.markdown(
                (
                    f"<div class='detail-card'>"
                    f"<div class='education-badge'>Detail Sekolah</div>"
                    f"<h1>{safe_name}</h1>"
                    f"<p class='detail-desc'>{safe_desc}</p>"
                    f"<div class='detail-meta'>"
                    f"<div class='detail-meta-item'>"
                    f"<div class='detail-meta-label'>Jenjang</div>"
                    f"<div class='detail-meta-value'>{safe_level}</div>"
                    f"</div>"
                    f"<div class='detail-meta-item'>"
                    f"<div class='detail-meta-label'>Lokasi</div>"
                    f"<div class='detail-meta-value'>{safe_address}</div>"
                    f"</div>"
                    f"</div>"
                    f"</div>"
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                (
                    "<div class='content-card'>"
                    "<h3>Fasilitas dan Layanan</h3>"
                    "<ul>"
                    "<li>Program pendidikan inklusi.</li>"
                    "<li>Guru pendamping khusus.</li>"
                    "<li>Konseling orang tua.</li>"
                    "<li>Lingkungan belajar yang ramah anak.</li>"
                    "</ul>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                (
                    "<div class='content-card'>"
                    "<h3>Catatan Penggunaan</h3>"
                    "<p>"
                    "Informasi sekolah pada fitur ini digunakan sebagai referensi awal "
                    "bagi caregiver. Caregiver tetap disarankan menghubungi pihak sekolah "
                    "untuk memastikan ketersediaan layanan, prosedur pendaftaran, dan "
                    "kebutuhan pendampingan anak."
                    "</p>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

            st.link_button(
                "Lihat Lokasi di Google Maps",
                sekolah_detail["maps"],
                use_container_width=True,
            )

            if sekolah_detail.get("wa"):
                st.link_button(
                    "Hubungi melalui WhatsApp",
                    sekolah_detail["wa"],
                    use_container_width=True,
                )

    markdown_html("</div>")
