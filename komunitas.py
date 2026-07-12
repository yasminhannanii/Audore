import html
import time
from textwrap import dedent

import streamlit as st

from database import init_db, register_user as db_register_user, login_user as db_login_user, get_all_users

KATEGORI_KOMUNITAS = [
    "Gangguan Psikologis Pendamping",
    "Kebutuhan Informasi",
    "Dukungan",
    "Masalah Lain",
]


def markdown_html(content):
    cleaned = dedent(content).strip()
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def apply_community_style():
    markdown_html(
        """
        <style>
        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"] {
            color-scheme: light;
        }

        .community-page {
            max-width: 1120px;
            margin: 0 auto;
        }

        .community-hero {
            background:
                radial-gradient(circle at top left, rgba(255, 221, 231, 0.95) 0%, transparent 36%),
                radial-gradient(circle at bottom right, rgba(221, 238, 255, 0.95) 0%, transparent 42%),
                linear-gradient(145deg, #FFFFFF 0%, #FFF9FB 100%);
            border: 1px solid rgba(214, 178, 192, 0.26);
            border-radius: 28px;
            box-shadow: 0 18px 42px rgba(115, 89, 103, 0.12);
            padding: 2.2rem 2.4rem;
            margin-bottom: 1.35rem;
        }

        .community-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(214, 151, 174, 0.22);
            border-radius: 999px;
            color: #9C4F70;
            font-size: 0.86rem;
            font-weight: 800;
            padding: 0.42rem 0.85rem;
            margin-bottom: 1rem;
        }

        .community-hero h1 {
            color: #2F2A38;
            font-size: 2.35rem;
            font-weight: 850;
            margin: 0 0 0.6rem 0;
            letter-spacing: 0;
        }

        .community-hero p {
            color: #635765;
            font-size: 1.05rem;
            line-height: 1.7;
            margin: 0;
        }

        .community-summary-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
            margin-top: 1.55rem;
        }

        .community-summary-item {
            background: rgba(255, 255, 255, 0.76);
            border: 1px solid rgba(214, 151, 174, 0.18);
            border-radius: 18px;
            padding: 1rem 1.1rem;
        }

        .community-summary-item strong {
            display: block;
            color: #2F2A38;
            font-size: 1.15rem;
            font-weight: 850;
            margin-bottom: 0.2rem;
        }

        .community-summary-item span {
            color: #746675;
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .community-section-heading {
            margin: 1.45rem 0 0.85rem 0;
        }

        .community-section-heading h2 {
            color: #2F2A38;
            font-size: 1.38rem;
            font-weight: 850;
            margin: 0;
            letter-spacing: 0;
        }

        .community-section-heading p {
            color: #746675;
            font-size: 0.95rem;
            line-height: 1.6;
            margin: 0.24rem 0 0 0;
        }

        .community-action-card {
            position: relative;
            overflow: hidden;
            border-radius: 22px;
            border: 1px solid rgba(255, 255, 255, 0.72);
            box-shadow: 0 16px 32px rgba(76, 62, 72, 0.13);
            padding: 1.35rem;
            min-height: 16.5rem;
            margin-bottom: 0.75rem;
        }

        .community-tone-blue {
            background: linear-gradient(145deg, #DDEEFF 0%, #BFDFFF 100%);
        }

        .community-tone-pink {
            background: linear-gradient(145deg, #FFE1EC 0%, #FFC4D9 100%);
        }

        .community-tone-yellow {
            background: linear-gradient(145deg, #FFF1BE 0%, #FFE08A 100%);
        }

        .community-card-top {
            display: flex;
            gap: 0.85rem;
            align-items: flex-start;
            margin-bottom: 1.2rem;
        }

        .community-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 2.65rem;
            height: 2.65rem;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid rgba(255, 255, 255, 0.82);
            color: #3B3340;
            font-size: 0.82rem;
            font-weight: 850;
            flex-shrink: 0;
        }

        .community-tag {
            display: inline-block;
            background: rgba(255, 255, 255, 0.62);
            border: 1px solid rgba(255, 255, 255, 0.78);
            border-radius: 999px;
            color: #4F4652;
            font-size: 0.76rem;
            font-weight: 750;
            padding: 0.3rem 0.68rem;
            margin-bottom: 0.52rem;
        }

        .community-accent {
            width: 2.7rem;
            height: 0.28rem;
            border-radius: 999px;
            margin: 0 0 0.82rem 0;
        }

        .community-tone-blue .community-accent {
            background: #4F86C6;
        }

        .community-tone-pink .community-accent {
            background: #D16BA5;
        }

        .community-tone-yellow .community-accent {
            background: #D9A820;
        }

        .community-action-card h3 {
            color: #2F2A38;
            font-size: 1.28rem;
            font-weight: 850;
            margin: 0;
            letter-spacing: 0;
            line-height: 1.25;
        }

        .community-action-card p {
            color: #4F4652;
            font-size: 0.94rem;
            line-height: 1.6;
            margin: 0.35rem 0 1rem 0;
            min-height: 4.7rem;
        }

        .community-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.8rem;
        }

        .community-chip-row span {
            background: rgba(255, 255, 255, 0.64);
            border: 1px solid rgba(255, 255, 255, 0.78);
            border-radius: 999px;
            color: #5A505C;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 0.38rem 0.7rem;
        }

        .community-list-card {
            background: rgba(255, 255, 255, 0.90);
            border: 1px solid rgba(214, 151, 174, 0.15);
            border-radius: 22px;
            box-shadow: 0 16px 34px rgba(115, 89, 103, 0.08);
            padding: 1.15rem;
            margin-bottom: 1rem;
        }

        .community-list-card h3 {
            color: #2F2A38;
            font-size: 1.08rem;
            font-weight: 850;
            margin: 0 0 0.85rem 0;
        }

        .community-list-item {
            background: #FFFFFF;
            border: 1px solid rgba(214, 151, 174, 0.13);
            border-radius: 16px;
            padding: 0.85rem 0.95rem;
            margin-bottom: 0.65rem;
        }

        .community-list-item strong {
            display: block;
            color: #2F2A38;
            font-size: 0.95rem;
            font-weight: 850;
            margin-bottom: 0.18rem;
        }

        .community-list-item span {
            color: #746675;
            font-size: 0.88rem;
            line-height: 1.45;
        }

        .community-post-card {
            background: #FFFFFF;
            border: 1px solid rgba(214, 151, 174, 0.15);
            border-radius: 20px;
            box-shadow: 0 12px 26px rgba(115, 89, 103, 0.08);
            padding: 1rem 1.1rem;
            margin: 0.8rem 0;
        }

        .community-post-card strong {
            color: #2F2A38;
            font-size: 1rem;
        }

        .community-post-card em {
            color: #9C4F70;
            font-size: 0.9rem;
            font-style: normal;
            font-weight: 700;
        }

        .community-post-card p {
            color: #5F5560;
            line-height: 1.6;
            margin: 0.65rem 0 0 0;
        }

        .chat-left,
        .chat-right {
            display: flex;
            margin-bottom: 10px;
        }

        .chat-left {
            justify-content: flex-start;
        }

        .chat-right {
            justify-content: flex-end;
        }

        .chat-bubble-left,
        .chat-bubble-right {
            padding: 12px 14px;
            border-radius: 18px;
            max-width: 72%;
            line-height: 1.5;
            box-shadow: 0 8px 20px rgba(115, 89, 103, 0.08);
        }

        .chat-bubble-left {
            background: #FFF5FA;
            border-radius: 18px 18px 18px 5px;
            color: #4B4048;
        }

        .chat-bubble-right {
            background: #DDEEFF;
            border-radius: 18px 18px 5px 18px;
            color: #364455;
        }

        .chat-name-left {
            color: #D16BA5;
            font-weight: 850;
        }

        .chat-name-right {
            color: #4F86C6;
            font-weight: 850;
        }

        div[data-testid="stButton"] > button {
            border-radius: 999px;
            font-weight: 800;
            min-height: 2.7rem;
            box-shadow: 0 10px 22px rgba(115, 89, 103, 0.12);
        }

        div[data-testid="stButton"] > button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.96);
            color: #3A2E3F;
            border: 1px solid rgba(214, 151, 174, 0.24);
        }

        div[data-testid="stButton"] > button:hover {
            background: #FFF8FB;
            color: #B9577C;
            border: 1px solid rgba(214, 151, 174, 0.35);
        }

        @media (max-width: 760px) {
            .community-hero {
                padding: 1.55rem;
            }

            .community-hero h1 {
                font-size: 1.85rem;
            }

            .community-summary-grid {
                grid-template-columns: 1fr;
            }

            .community-action-card {
                min-height: auto;
            }

            .community-action-card p {
                min-height: auto;
            }

            .chat-bubble-left,
            .chat-bubble-right {
                max-width: 88%;
            }
        }
        </style>
        """
    )


def respon_ai(kategori):
    if kategori == "Gangguan Psikologis Pendamping":
        return """
        Terima kasih telah berbagi pengalaman Anda.

        Keluhan ini berkaitan dengan kondisi psikologis pendamping, seperti rasa lelah,
        khawatir, stres, sedih, atau merasa terbebani saat mendampingi anak.

        Beberapa langkah yang dapat dicoba:
        - Luangkan waktu untuk beristirahat.
        - Ceritakan kondisi Anda kepada keluarga atau orang terdekat.
        - Bergabung dengan komunitas caregiver agar tidak merasa sendiri.
        - Pertimbangkan bantuan profesional jika rasa lelah atau cemas semakin mengganggu.
        """

    if kategori == "Kebutuhan Informasi":
        return """
        Keluhan ini berkaitan dengan kebutuhan informasi mengenai ASD, terapi,
        layanan kesehatan, pendidikan, atau cara mendampingi anak.

        Anda dapat menggunakan fitur Edukasi untuk membaca informasi yang lebih terarah
        mengenai perkembangan anak, terapi, pengasuhan, dan pendidikan inklusif.
        """

    if kategori == "Dukungan":
        return """
        Keluhan ini menunjukkan adanya kebutuhan dukungan sosial dan emosional.

        Komunitas dapat menjadi ruang untuk berbagi cerita, memperoleh masukan,
        dan saling menguatkan dengan caregiver lain yang memiliki pengalaman serupa.
        """

    if kategori == "Masalah Lain":
        return """
        Terima kasih telah berbagi pengalaman Anda.

        Keluhan ini belum termasuk dalam kategori utama, tetapi tetap penting untuk
        didiskusikan. Anda dapat menjelaskan kondisi lebih detail agar caregiver lain
        atau Audore Assistant dapat memberikan tanggapan yang lebih sesuai.
        """

    return "Terima kasih telah berbagi pengalaman Anda."


def run_komunitas():
    apply_community_style()

    if "posts" not in st.session_state:
        st.session_state.posts = [
            {
                "nama": "Diandra A",
                "kategori": "Gangguan Psikologis Pendamping",
                "isi": "Saya merasa kelelahan mendampingi terapi anak setiap hari. Apakah ada yang mengalami hal serupa?",
                "user_post": False,
                "likes": 3,
                "replies": [
                    {
                        "nama": "Anastasia",
                        "isi": "Saya juga pernah mengalami hal yang sama.",
                    }
                ],
            },
            {
                "nama": "Dirga",
                "kategori": "Kebutuhan Informasi",
                "isi": "Ada yang memiliki pengalaman mengenai terapi wicara untuk anak ASD?",
                "user_post": False,
                "likes": 2,
                "replies": [],
            },
        ]

    if "group_chat" not in st.session_state:
        st.session_state.group_chat = [
            {
                "nama": "Amanda",
                "pesan": "Hai semuanya! Ada yang punya tips agar anak lebih fokus saat belajar?",
                "user": False,
            },
            {
                "nama": "Sabrina",
                "pesan": "Halo, saya biasanya membuat jadwal belajar singkat lalu diselingi istirahat.",
                "user": False,
            },
            {
                "nama": "Hani",
                "pesan": "Kalau saya biasanya membuat rutinitas yang konsisten untuk anak saya.",
                "user": False,
            },
        ]

    if "menu_komunitas" not in st.session_state:
        st.session_state.menu_komunitas = "Home"

    if st.session_state.menu_komunitas == "Home":
        total_replies = sum(len(post["replies"]) for post in st.session_state.posts)
        total_likes = sum(post["likes"] for post in st.session_state.posts)

        markdown_html(
            f"""
            <div class="community-page">
                <section class="community-hero">
                    <span class="community-badge">Komunitas Audore</span>
                    <h1>Forum Komunitas</h1>
                    <p>
                        Ruang aman bagi caregiver anak dengan Autism Spectrum Disorder (ASD)
                        untuk saling berbagi cerita, bertukar informasi, dan mendapatkan dukungan
                        dari sesama pendamping.
                    </p>
                    <div class="community-summary-grid">
                        <div class="community-summary-item">
                            <strong>{len(st.session_state.posts)}</strong>
                            <span>Diskusi aktif</span>
                        </div>
                        <div class="community-summary-item">
                            <strong>125</strong>
                            <span>Caregiver tergabung</span>
                        </div>
                        <div class="community-summary-item">
                            <strong>{total_replies + total_likes}</strong>
                            <span>Interaksi komunitas</span>
                        </div>
                    </div>
                </section>

                <div class="community-section-heading">
                    <h2>Pilih Ruang Komunitas</h2>
                    <p>Mulai dari membuat cerita, membaca diskusi terbaru, atau berbincang langsung di group chat.</p>
                </div>
            </div>
            """
        )

        cards = [
            {
                "tone": "community-tone-blue",
                "icon": "01",
                "tag": "Berbagi Cerita",
                "title": "Buat Postingan",
                "body": "Tulis pengalaman, pertanyaan, atau dukungan yang ingin dibagikan kepada caregiver lainnya.",
                "chips": ["Cerita", "Pertanyaan", "Dukungan"],
                "menu": "Buat Postingan",
                "key": "buat",
                "button": "Buka Buat Postingan",
            },
            {
                "tone": "community-tone-pink",
                "icon": "02",
                "tag": "Forum Diskusi",
                "title": "Postingan Terbaru",
                "body": "Lihat pengalaman terbaru, beri tanggapan, dan temukan sudut pandang dari keluarga lain.",
                "chips": ["Diskusi", "Balasan", "Like"],
                "menu": "Postingan Terbaru",
                "key": "posting",
                "button": "Buka Postingan",
            },
            {
                "tone": "community-tone-yellow",
                "icon": "03",
                "tag": "Obrolan Langsung",
                "title": "Group Chat",
                "body": "Ngobrol santai dengan caregiver lain untuk berbagi tips harian dan saling menguatkan.",
                "chips": ["Chat", "Tips", "Teman Cerita"],
                "menu": "Group Chat",
                "key": "chat",
                "button": "Buka Group Chat",
            },
        ]

        col1, col2, col3 = st.columns(3)

        for col, card in zip((col1, col2, col3), cards):
            chip_html = "".join(
                f"<span>{html.escape(chip)}</span>"
                for chip in card["chips"]
            )

            with col:
                markdown_html(
                    f"""
                    <div class="community-action-card {card['tone']}">
                        <div class="community-card-top">
                            <div class="community-icon">{card['icon']}</div>
                            <div>
                                <span class="community-tag">{html.escape(card['tag'])}</span>
                                <h3>{html.escape(card['title'])}</h3>
                            </div>
                        </div>
                        <div class="community-accent"></div>
                        <p>{html.escape(card['body'])}</p>
                        <div class="community-chip-row">{chip_html}</div>
                    </div>
                    """
                )

                if st.button(
                    card["button"],
                    key=f"btn_{card['key']}",
                    use_container_width=True,
                ):
                    st.session_state.menu_komunitas = card["menu"]
                    st.rerun()

        markdown_html(
            """
            <div class="community-page">
                <div class="community-section-heading">
                    <h2>Yang Sedang Dibahas</h2>
                    <p>Topik dan agenda dibuat ringkas agar caregiver cepat menemukan ruang yang sesuai.</p>
                </div>
            </div>
            """
        )

        kiri, kanan = st.columns(2)

        with kiri:
            topik = [
                (
                    "Gangguan Psikologis Pendamping",
                    "Diskusi tentang rasa lelah, khawatir, stres, sedih, burnout, dan tekanan selama mendampingi anak.",
                ),
                (
                    "Kebutuhan Informasi",
                    "Pertanyaan seputar ASD, terapi, layanan kesehatan, pendidikan, dan cara mendampingi anak.",
                ),
                (
                    "Dukungan",
                    "Ruang untuk mencari teman cerita, saling menguatkan, dan berbagi pengalaman sesama caregiver.",
                ),
                (
                    "Masalah Lain",
                    "Topik lain yang belum termasuk kategori utama, tetapi tetap relevan untuk dibagikan.",
                ),
            ]

            item_html = "".join(
                f"""
                <div class="community-list-item">
                    <strong>{html.escape(title)}</strong>
                    <span>{html.escape(desc)}</span>
                </div>
                """
                for title, desc in topik
            )

            markdown_html(
                f"""
                <div class="community-list-card">
                    <h3>Kategori Masalah</h3>
                    {item_html}
                </div>
                """
            )

        with kanan:
            info = [
                ("Webinar Parenting ASD", "Sesi edukasi pendek mengenai strategi pendampingan anak."),
                ("Sharing Session Caregiver", "Ruang cerita bersama caregiver lain dalam suasana santai."),
                ("Seminar Pendidikan Inklusif", "Informasi seputar dukungan belajar dan sekolah inklusi."),
            ]

            item_html = "".join(
                f"""
                <div class="community-list-item">
                    <strong>{html.escape(title)}</strong>
                    <span>{html.escape(desc)}</span>
                </div>
                """
                for title, desc in info
            )

            markdown_html(
                f"""
                <div class="community-list-card">
                    <h3>Informasi Penting</h3>
                    {item_html}
                </div>
                """
            )

    elif st.session_state.menu_komunitas == "Buat Postingan":
        if st.button("Kembali"):
            st.session_state.menu_komunitas = "Home"
            st.rerun()

        markdown_html(
            """
            <div class="community-page">
                <div class="community-section-heading">
                    <h2>Buat Postingan</h2>
                    <p>Bagikan pengalaman, pertanyaan, atau dukungan kepada caregiver lainnya.</p>
                </div>
            </div>
            """
        )

        nama = st.text_input("Nama Pengguna")

        kategori = st.selectbox(
            "Kategori Masalah",
            KATEGORI_KOMUNITAS,
        )

        isi_post = st.text_area("Bagikan cerita atau pertanyaan Anda")

        if st.button("Posting", use_container_width=True):
            if nama and isi_post:
                st.session_state.posts.insert(
                    0,
                    {
                        "nama": nama,
                        "kategori": kategori,
                        "isi": isi_post,
                        "user_post": True,
                        "likes": 0,
                        "replies": [],
                    },
                )

                st.success("Postingan berhasil ditambahkan.")
                st.rerun()
            else:
                st.warning("Nama dan isi postingan perlu diisi terlebih dahulu.")

        st.markdown("### Postingan Saya")

        for i, post in enumerate(st.session_state.posts):
            if post.get("user_post", False):
                markdown_html(
                    f"""
                    <div class="community-post-card">
                        <strong>{html.escape(post['nama'])}</strong><br>
                        <em>{html.escape(post['kategori'])}</em>
                        <p>{html.escape(post['isi'])}</p>
                    </div>
                    """
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "Konsultasi dengan Audore Assistant",
                        key=f"ai_{i}",
                        use_container_width=True,
                    ):
                        st.info(respon_ai(post["kategori"]))

                with col2:
                    if st.button(
                        "Hapus Postingan",
                        key=f"hapus_{i}",
                        use_container_width=True,
                    ):
                        st.session_state.posts.pop(i)
                        st.rerun()

    elif st.session_state.menu_komunitas == "Postingan Terbaru":
        if st.button("Kembali"):
            st.session_state.menu_komunitas = "Home"
            st.rerun()

        markdown_html(
            """
            <div class="community-page">
                <div class="community-section-heading">
                    <h2>Postingan Terbaru</h2>
                    <p>Baca cerita caregiver lain, beri dukungan, dan kirimkan balasan.</p>
                </div>
            </div>
            """
        )

        for i, post in enumerate(st.session_state.posts):
            markdown_html(
                f"""
                <div class="community-post-card">
                    <strong>{html.escape(post['nama'])}</strong><br>
                    <em>{html.escape(post['kategori'])}</em>
                    <p>{html.escape(post['isi'])}</p>
                </div>
                """
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    f"Like ({post['likes']})",
                    key=f"like_{i}",
                    use_container_width=True,
                ):
                    st.session_state.posts[i]["likes"] += 1
                    st.rerun()

            with col2:
                st.write(f"{len(post['replies'])} Balasan")

            nama_balasan = st.text_input("Nama", key=f"reply_name_{i}")
            balasan = st.text_input("Tulis balasan", key=f"reply_input_{i}")

            if st.button(
                "Kirim Balasan",
                key=f"reply_btn_{i}",
                use_container_width=True,
            ):
                if nama_balasan and balasan:
                    st.session_state.posts[i]["replies"].append(
                        {
                            "nama": nama_balasan,
                            "isi": balasan,
                        }
                    )

                    st.rerun()
                else:
                    st.warning("Nama dan balasan perlu diisi terlebih dahulu.")

            for reply in post["replies"]:
                st.info(f"{reply['nama']}: {reply['isi']}")

            st.markdown("---")

    elif st.session_state.menu_komunitas == "Group Chat":
        if st.button("Kembali"):
            st.session_state.menu_komunitas = "Home"
            st.rerun()

        markdown_html(
            """
            <div class="community-page">
                <div class="community-section-heading">
                    <h2>Group Chat Caregiver</h2>
                    <p>Ruang diskusi santai antar caregiver anak ASD.</p>
                </div>
            </div>
            """
        )

        st.markdown("---")

        for chat in st.session_state.group_chat:
            nama = html.escape(chat["nama"])
            pesan = html.escape(chat["pesan"])

            if chat.get("user", False):
                markdown_html(
                    f"""
                    <div class="chat-right">
                        <div class="chat-bubble-right">
                            <span class="chat-name-right">Anda</span><br>
                            {pesan}
                        </div>
                    </div>
                    """
                )
            else:
                markdown_html(
                    f"""
                    <div class="chat-left">
                        <div class="chat-bubble-left">
                            <span class="chat-name-left">{nama}</span><br>
                            {pesan}
                        </div>
                    </div>
                    """
                )

        st.markdown("---")

        pesan_chat = st.text_input(
            "Pesan",
            placeholder="Tulis pesan...",
            key="group_chat_input",
        )

        if st.button("Kirim Pesan", key="btn_group_chat", use_container_width=True):
            if pesan_chat.strip():
                st.session_state.group_chat.append(
                    {
                        "nama": "Anda",
                        "pesan": pesan_chat,
                        "user": True,
                    }
                )

                kategori = st.session_state.get("kategori_masalah", "Masalah Lain")

                if kategori == "Gangguan Psikologis Pendamping":
                    bot_reply = (
                        "Berdasarkan hasil identifikasi sebelumnya, keluhan Anda berkaitan "
                        "dengan kondisi psikologis caregiver. Merasa lelah, cemas, atau stres "
                        "merupakan hal yang cukup sering dialami caregiver anak ASD. Jangan ragu "
                        "untuk beristirahat, berbagi cerita dengan keluarga maupun komunitas, "
                        "serta mencari bantuan profesional apabila diperlukan."
                    )

                elif kategori == "Kebutuhan Informasi":
                    bot_reply = (
                        "Keluhan Anda berkaitan dengan kebutuhan informasi mengenai ASD. "
                        "Kami menyarankan untuk memanfaatkan fitur Edukasi agar memperoleh "
                        "informasi mengenai terapi, pengasuhan, pendidikan, serta perkembangan anak ASD."
                    )

                elif kategori == "Dukungan":
                    bot_reply = (
                        "Keluhan Anda menunjukkan bahwa Anda membutuhkan dukungan sosial. "
                        "Forum komunitas merupakan tempat yang tepat untuk berbagi pengalaman "
                        "dengan caregiver lain yang memiliki kondisi serupa. Semoga Anda "
                        "memperoleh dukungan yang dibutuhkan."
                    )

                else:
                    bot_reply = (
                        "Terima kasih telah berbagi pengalaman. Semoga para pendamping lain "
                        "juga dapat memberikan masukan dan pengalaman yang bermanfaat."
                    )

                with st.spinner("Audore Support sedang mengetik..."):
                    time.sleep(5)

                st.session_state.group_chat.append(
                    {
                        "nama": "Audore Support",
                        "pesan": bot_reply,
                        "user": False,
                        "bot": True,
                    }
                )

                st.rerun()
            else:
                st.warning("Pesan tidak boleh kosong.")
