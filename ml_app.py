import html
import os
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from database import init_db, save_chat_message, load_chat_sessions, delete_chat_history

import nltk
from nltk.corpus import stopwords

try:
    INDONESIAN_STOPWORDS = set(stopwords.words("indonesian"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    INDONESIAN_STOPWORDS = set(stopwords.words("indonesian"))

RANDOM_STATE = 42
TEST_SIZE = 0.25
DATASET_FILENAME = "dataset_keluhan_pasien_masalah_sudah_digabungin.xlsx"
REQUIRED_COLUMNS = {
    "Postingan Keluhan",
    "Kategori Masalah",
    "Fitur",
    "Penjelasan masalah + kasus",
    "FLAG CRISIS",
    "SKOR URGENSI",
}

PROBLEM_LABEL_TO_ID = {
    "Dukungan": 0,
    "Gangguan Psikologis Pendamping": 1,
    "Kebutuhan Informasi": 2,
    "Masalah Lain": 3,
}

PROBLEM_TO_FEATURE = {
    "Gangguan Psikologis Pendamping": "Konsultasi",
    "Dukungan": "Komunitas",
    "Kebutuhan Informasi": "Edukasi",
    "Masalah Lain": "Konsultasi",
    "Kondisi Krisis": "Konsultasi Darurat",
}

FEATURE_TO_URGENCY = {
    "Edukasi": 1,
    "Komunitas": 2,
    "Konsultasi": 3,
    "Konsultasi Darurat": 4,
}

CRISIS_KEYWORDS = (
    "bunuh diri",
    "mengakhiri hidup",
    "menyakiti diri",
    "ingin mati",
)

NON_INFORMATIVE_TOKENS = {'akan',
 'akhir',
 'aku',
 'anak',
 'anda',
 'atau',
 'bagi',
 'bahwa',
 'banyak',
 'belum',
 'bisa',
 'cukup',
 'dalam',
 'dan',
 'dapat',
 'dari',
 'dengan',
 'di',
 'dia',
 'hari',
 'harus',
 'ingin',
 'ini',
 'itu',
 'jadi',
 'juga',
 'karena',
 'ke',
 'kerap',
 'ketika',
 'kurang',
 'lain',
 'lebih',
 'masih',
 'mau',
 'membuat',
 'membutuhkan',
 'memengaruhi',
 'mengalami',
 'menjadi',
 'menyelesaikan',
 'merasa',
 'mereka',
 'miliki',
 'mudah',
 'mulai',
 'oleh',
 'orang',
 'pada',
 'saat',
 'saja',
 'salah',
 'sangat',
 'satu',
 'saya',
 'sebagai',
 'sedang',
 'sehingga',
 'seperti',
 'sering',
 'sesuai',
 'setelah',
 'sudah',
 'telah',
 'tentang',
 'terbesar',
 'terkait',
 'tersebut',
 'terus',
 'tidak',
 'untuk',
 'yang'}

PROBABILITY_LABELS = [
    "Dukungan",
    "Gangguan Psikologis Pendamping",
    "Kebutuhan Informasi",
    "Masalah Lain",
]

RESPONSE_BY_PROBLEM = {
    "Kebutuhan Informasi": (
        "Kesulitan memperoleh informasi yang jelas mengenai ASD dapat membuat "
        "caregiver merasa bingung dalam mengambil keputusan terkait pengasuhan "
        "maupun terapi. Memahami kondisi anak secara lebih baik dapat membantu "
        "meningkatkan kepercayaan diri dalam mendampingi anak sehari-hari. Anda "
        "dapat mengakses fitur Edukasi untuk memperoleh informasi dan materi yang relevan."
    ),
    "Dukungan": (
        "Kurangnya dukungan dari lingkungan sekitar dapat membuat caregiver merasa "
        "sendirian dalam menghadapi berbagai tantangan pengasuhan. Berbagi pengalaman "
        "dengan orang lain yang memiliki situasi serupa sering kali membantu mengurangi "
        "beban emosional dan memberikan sudut pandang baru. Anda dapat memanfaatkan "
        "fitur Forum Komunitas untuk terhubung dengan caregiver lainnya."
    ),
    "Gangguan Psikologis Pendamping": (
        "Saya memahami bahwa tanggung jawab pengasuhan yang terus-menerus dapat "
        "menimbulkan kelelahan fisik dan emosional. Banyak caregiver mengalami "
        "tekanan ketika harus membagi waktu antara kebutuhan anak dan aktivitas "
        "sehari-hari. Anda dapat memanfaatkan fitur Konsultasi untuk berdiskusi "
        "lebih lanjut mengenai strategi pengelolaan stres dan dukungan yang sesuai "
        "dengan kondisi Anda."
    ),
    "Masalah Lain": (
        "Untuk informasi lebih lanjut mengenai masalah tersebut, silakan melakukan konsultasi."
    ),
}

CRISIS_RESPONSE = (
    "Terima kasih telah berbagi cerita. Kondisi yang Anda sampaikan memerlukan "
    "bantuan segera dan tidak sebaiknya menunggu jadwal konsultasi. Jangan berada "
    "sendirian. Hubungi orang terdekat yang dapat mendampingi Anda, lalu datangi "
    "IGD atau fasilitas kesehatan terdekat, atau hubungi layanan darurat setempat. "
    "Apabila terdapat benda, obat, atau alat yang dapat digunakan untuk menyakiti "
    "diri, jauhkan benda tersebut dari jangkauan dan minta orang lain untuk menyimpannya."
)

# Hanya istilah umum yang tidak merepresentasikan masalah yang dihapus.
KNOWLEDGE_BASE_KEYWORD = {'Dukungan': {'saya khawatir': 1.9063424049353728,
              'dipahami': 1.7339014932066943,
              'merasa kelelahan': 1.5863227085334601,
              'tidur karena': 1.4293235744106776,
              'kurang tidur': 1.4293235744106776,
              'kelelahan secara': 1.4280565637068505,
              'secara fisik': 1.4256914230922304,
              'fisik': 1.4256914230922304,
              'dipahami ketika': 1.4254388073692734,
              'tidak dipahami': 1.4254388073692734,
              'fisik karena': 1.3843116965454685,
              'kelelahan': 1.3316952812824383,
              'kewalahan dengan': 1.2954049832376555,
              'khawatir': 1.2416960789529972,
              'pengalaman': 1.2347160175687697,
              'ingin mengetahui': 1.1641004864251874,
              'kesehatan': 1.1293940334233254,
              'saya menurun': 1.1293940334233254,
              'kondisi kesehatan': 1.1293940334233254,
              'menurun': 1.1293940334233254,
              'kesehatan saya': 1.1293940334233254,
              'membuat kondisi': 1.1293940334233254,
              'mengalami kesulitan': 1.0935349747379308,
              'tidur': 1.084784875379075,
              'dukungan': 1.042812340813576,
              'membutuhkan informasi': 1.022616272252256},
 'Gangguan Psikologis Pendamping': {'kesulitan mengendalikan': 2.211839542735958,
                                    'emosi': 2.211839542735958,
                                    'mengendalikan': 2.211839542735958,
                                    'mengendalikan emosi': 2.211839542735958,
                                    'lelah': 1.8493161744421953,
                                    'merasa khawatir': 1.7065317196838077,
                                    'sangat lelah': 1.6347586444636,
                                    'sedih': 1.3705232199022603,
                                    'merasa sedih': 1.3705232199022603,
                                    'sulit merasa': 1.1919062372537759,
                                    'merasa tenang': 1.1919062372537759,
                                    'tenang': 1.1919062372537759,
                                    'tidak sanggup': 1.160329043321004,
                                    'sanggup menghadapi': 1.160329043321004,
                                    'sanggup': 1.160329043321004,
                                    'emosi saat': 1.1530421048001116,
                                    'menyerah': 1.1121473955370855,
                                    'ingin menyerah': 1.1121473955370855,
                                    'memikirkan': 1.1077710386421629,
                                    'cemas': 1.1055372713048555,
                                    'merasa cemas': 1.1055372713048555,
                                    'kondisi anak': 1.0889312553732495,
                                    'terbebani': 1.0285515011645074,
                                    'merasa terbebani': 1.0285515011645074,
                                    'terapi anak': 1.0227468812562892},
 'Kebutuhan Informasi': {'bingung': 2.2194837342956646,
                         'bantuan': 2.2067312226526345,
                         'layanan': 2.0035709380569733,
                         'mengakses layanan': 1.8673901008077394,
                         'mengakses': 1.8673901008077394,
                         'cara': 1.8183839237999897,
                         'mencari': 1.675449929174094,
                         'dengan kebutuhan': 1.6192738692624784,
                         'informasi mengenai': 1.5782442490462363,
                         'mencari informasi': 1.526516540901937,
                         'sedang mencari': 1.526516540901937,
                         'masih bingung': 1.4891362856994836,
                         'profesional': 1.4869957658590485,
                         'bantuan profesional': 1.4869957658590485,
                         'terapi yang': 1.4743893389834835,
                         'mengenai cara': 1.3833444995158333,
                         'kesulitan mengakses': 1.3824832639519327,
                         'mendapatkan bantuan': 1.3820196995793643,
                         'informasi': 1.341134536334279,
                         'bingung bagaimana': 1.313177003843823,
                         'bagaimana': 1.313177003843823,
                         'panduan untuk': 1.2946462706428485,
                         'panduan': 1.2946462706428485,
                         'membutuhkan panduan': 1.2946462706428485,
                         'layanan karena': 1.2503923195005062,
                         'membutuhkan bantuan': 1.1809079463201573,
                         'kesulitan mendapatkan': 1.1635622946438045,
                         'menghadapinya': 1.1590160140854668,
                         'untuk menghadapinya': 1.1590160140854668,
                         'layanan yang': 1.1166755852906052,
                         'kesulitan': 1.0824323491111847,
                         'bantuan karena': 1.0797679581269826,
                         'bergantung': 1.0785469178629103,
                         'bergantung pada': 1.0785469178629103,
                         'untuk mengelola': 1.0530935447900753,
                         'mengelola': 1.0530935447900753,
                         'saya kesulitan': 1.0520091978565467,
                         'saya bingung': 1.039940994250975,
                         'bingung dan': 1.039940994250975,
                         'profesional untuk': 1.0353253478089326,
                         'tantangan terbesar': 1.0123684334139387,
                         'satu tantangan': 1.0123684334139387,
                         'rutinitas mendampingi': 1.004304813185115},
 'Masalah Lain': {'pekerjaan': 2.886837588149022,
                  'bekerja': 1.9592360788067444,
                  'rumah': 1.4631538231847534,
                  'jam': 1.435330627754802,
                  'menghambat': 1.416625176292272,
                  'kerja': 1.373077263270679,
                  'saya kesulitan': 1.330122499910492,
                  'administrasi': 1.2775015247808241,
                  'tempat tinggal': 1.1671928976751675,
                  'tinggal yang': 1.1671928976751675,
                  'tinggal': 1.1671928976751675,
                  'sering menghambat': 1.1629449235474878,
                  'sering bermasalah': 1.1591627182167472,
                  'bermasalah': 1.1591627182167472,
                  'stabil': 1.1546153356172089,
                  'kesulitan menjaga': 1.1088810979294734,
                  'internet': 1.1020193303724248,
                  'sistem': 1.0821721307023147,
                  'mengganggu': 1.0729742302768552,
                  'mengganggu aktivitas': 1.0729742302768552,
                  'anggaran': 1.0373402467119726,
                  'membuat pekerjaan': 1.0358756121456203}}

def _knowledge_base_has_terms(knowledge_base):
    """Periksa apakah knowledge base berisi kategori dan keyword berbobot valid."""
    if not isinstance(knowledge_base, dict):
        return False

    expected_categories = set(PROBLEM_LABEL_TO_ID)
    if set(knowledge_base) != expected_categories:
        return False

    for category in expected_categories:
        terms = knowledge_base.get(category)
        if not isinstance(terms, dict) or not terms:
            return False
        for term, weight in terms.items():
            if not isinstance(term, str) or not term.strip():
                return False
            try:
                if float(weight) <= 1.0:
                    return False
            except (TypeError, ValueError):
                return False

    return True


def _normalize_knowledge_base(knowledge_base):
    """Normalisasi tipe data dan urutkan keyword berdasarkan bobot."""
    normalized = {}
    for category in PROBLEM_LABEL_TO_ID:
        terms = knowledge_base.get(category, {})
        valid_terms = {}
        for term, weight in terms.items():
            clean_term = str(term).strip()
            numeric_weight = float(weight)
            if numeric_weight <= 1.0:
                continue
            if not _is_informative_term(clean_term):
                continue
            valid_terms[clean_term] = numeric_weight

        normalized[category] = dict(
            sorted(valid_terms.items(), key=lambda item: (-item[1], item[0]))
        )
    return normalized


def clean(text):
    """
    Preprocessing sesuai notebook:
    1. Menghapus karakter selain huruf.
    2. Mengubah teks menjadi huruf kecil.
    3. Menghapus stopword bahasa Indonesia.
    4. Tidak melakukan stemming.
    """
    text = "" if text is None else str(text)

    # Menghapus karakter selain huruf dan spasi
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    # Case folding dan menghapus spasi berlebih
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)

    # Stopword removal
    words = text.split()
    words = [
        word
        for word in words
        if word not in INDONESIAN_STOPWORDS
    ]

    return " ".join(words)

def basic_clean(text):
    """
    Normalisasi dasar tanpa menghapus stopword.
    Digunakan untuk deteksi frasa krisis.
    """
    text = "" if text is None else str(text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = text.lower().strip()
    return re.sub(r"\s+", " ", text)


def resolve_dataset_path():
    env_path = os.getenv("AUDORE_DATASET_PATH", "").strip()
    candidates = []
    if env_path:
        candidates.append(Path(env_path).expanduser())

    script_dir = Path(__file__).resolve().parent
    current_dir = Path.cwd()
    search_dirs = [
        current_dir,
        script_dir,
        current_dir / "data",
        script_dir / "data",
        current_dir / "dataset",
        script_dir / "dataset",
    ]

    for directory in search_dirs:
        candidates.append(directory / DATASET_FILENAME)
        candidates.extend(sorted(directory.glob("dataset_keluhan_pasien_masalah_sudah_digabungin*.xlsx")))

    checked = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate
        if resolved in checked:
            continue
        checked.add(resolved)
        if candidate.is_file():
            return candidate

    locations = "\n".join(f"- {path}" for path in search_dirs)
    raise FileNotFoundError(
        f"Dataset '{DATASET_FILENAME}' tidak ditemukan. Letakkan file pada salah satu lokasi berikut:\n"
        f"{locations}\nAtau isi AUDORE_DATASET_PATH dengan lokasi dataset."
    )


def load_training_data(dataset_path):
    df = pd.read_excel(dataset_path)
    missing_columns = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing_columns:
        raise ValueError("Kolom dataset belum lengkap: " + ", ".join(missing_columns))

    df = df.copy()
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    for column in ["Postingan Keluhan", "Kategori Masalah", "Fitur", "Penjelasan masalah + kasus", "FLAG CRISIS"]:
        df[column] = df[column].astype(str).str.strip()
    df["SKOR URGENSI"] = pd.to_numeric(df["SKOR URGENSI"], errors="coerce")
    return df


def _validate_problem_labels(series):
    normalized = series.astype(str).str.strip()
    unknown = sorted(set(normalized.unique()).difference(PROBLEM_LABEL_TO_ID))
    if unknown:
        raise ValueError("Label kategori masalah tidak sesuai notebook: " + "; ".join(unknown))
    return normalized.map(PROBLEM_LABEL_TO_ID).astype(int)


def _aggregate_ovo_class_weights(model, n_classes, n_features):
    """Agregasi koefisien SVC one-vs-one sama dengan sel analisis notebook."""
    coefficients = model.coef_.toarray()
    class_weights = np.zeros((n_classes, n_features), dtype=float)
    pair_index = 0
    for class_i in range(n_classes):
        for class_j in range(class_i + 1, n_classes):
            class_weights[class_i] += coefficients[pair_index]
            class_weights[class_j] -= coefficients[pair_index]
            pair_index += 1
    return class_weights


def _is_informative_term(term):
    tokens = str(term).strip().split()
    return bool(tokens) and any(token not in NON_INFORMATIVE_TOKENS for token in tokens)


def _build_keyword_knowledge_base(vectorizer, model):
    feature_names = vectorizer.get_feature_names_out()
    class_weights = _aggregate_ovo_class_weights(
        model,
        n_classes=len(PROBLEM_LABEL_TO_ID),
        n_features=len(feature_names),
    )
    id_to_label = {value: key for key, value in PROBLEM_LABEL_TO_ID.items()}
    knowledge_base = {}

    for class_id in range(len(PROBLEM_LABEL_TO_ID)):
        category = id_to_label[class_id]
        category_terms = {}
        for feature_index, term in enumerate(feature_names):
            term = str(term).strip()
            weight = float(class_weights[class_id, feature_index])
            if weight <= 1.0:
                continue
            if not _is_informative_term(term):
                continue
            category_terms[term] = weight

        knowledge_base[category] = dict(
            sorted(category_terms.items(), key=lambda item: (-item[1], item[0]))
        )

    return knowledge_base

@st.cache_resource(show_spinner="Menyiapkan knowledge base Audore...")
def initialize_keyword_resources(dataset_path_string, dataset_mtime_ns):
    global KNOWLEDGE_BASE_KEYWORD

    del dataset_mtime_ns
    dataset_path = Path(dataset_path_string)
    df = load_training_data(dataset_path)

    x = df["Postingan Keluhan"].astype(str)
    y = _validate_problem_labels(df["Kategori Masalah"])
    x_train, _x_test, y_train, _y_test = train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    x_train_clean = x_train.apply(clean)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    x_train_tfidf = vectorizer.fit_transform(x_train_clean)

    model = SVC(random_state=RANDOM_STATE, probability=False, kernel="linear")
    model.fit(x_train_tfidf, y_train)

    knowledge_base = _normalize_knowledge_base(KNOWLEDGE_BASE_KEYWORD)
    if not _knowledge_base_has_terms(knowledge_base):
        raise ValueError(
            "KNOWLEDGE_BASE_KEYWORD di ml_app.py kosong atau tidak valid."
        )

    return {
        "knowledge_base": knowledge_base,
        "vectorizer": vectorizer,
        "model": model,
        "dataset_path": str(dataset_path),
        "row_count": int(len(df)),
    }


def _contains_term(cleaned_text, term):
    pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
    return re.search(pattern, cleaned_text) is not None


def _detect_crisis(cleaned_text):
    return [term for term in CRISIS_KEYWORDS if _contains_term(cleaned_text, term)]


def _weighted_scores_to_probabilities(weighted_scores, fallback_label=None):
    """
    Ubah hasil weighted scoring menjadi nilai probabilitas.

    Setiap skor kategori dibagi dengan total seluruh skor positif sehingga
    jumlah probabilitas menjadi 1 atau 100%. Jika tidak ada keyword yang
    cocok, kategori fallback diberi probabilitas 100%.
    """
    labels = list(PROBABILITY_LABELS)
    for label in weighted_scores:
        if label not in labels:
            labels.append(label)

    normalized_scores = {}
    for label in labels:
        try:
            score = float(weighted_scores.get(label, 0.0))
        except (TypeError, ValueError):
            score = 0.0
        normalized_scores[label] = max(0.0, score)

    total_score = sum(normalized_scores.values())

    if total_score > 0:
        return {
            label: score / total_score
            for label, score in normalized_scores.items()
        }

    probabilities = {label: 0.0 for label in labels}
    if fallback_label in probabilities:
        probabilities[fallback_label] = 1.0

    return probabilities


def classify_keluhan_weighted(original_text, resources):
    basic_text = basic_clean(original_text)
    cleaned_text = clean(original_text)

    if not basic_text:
        raise ValueError(
            "Keluhan tidak memuat karakter alfabet yang dapat diproses."
        )

    # Pemeriksaan krisis menggunakan teks yang belum dihapus stopword-nya.
    crisis_matches = _detect_crisis(basic_text)

    if crisis_matches:
        weighted_scores = {
            "Kondisi Krisis": 4.0,
        }
        probabilities = _weighted_scores_to_probabilities(
            weighted_scores,
            fallback_label="Kondisi Krisis",
        )

        return {
            "kategori_masalah": "Kondisi Krisis",
            "fitur": "Konsultasi Darurat",
            "respon": CRISIS_RESPONSE,
            "skor_urgensi": 4,
            "crisis_flag": "YES",
            "matched_keywords": crisis_matches,
            "weighted_scores": weighted_scores,
            "probabilities": probabilities,
        }

    # Menyiapkan skor dan daftar keyword untuk setiap kategori.
    category_scores = {
        category: 0.0
        for category in PROBLEM_LABEL_TO_ID
    }

    matches_by_category = {
        category: []
        for category in PROBLEM_LABEL_TO_ID
    }

    knowledge_base = resources["knowledge_base"]

    # Pencocokan keyword dan penjumlahan bobot.
    for category, weighted_terms in knowledge_base.items():
        for term, weight in weighted_terms.items():
            if _contains_term(cleaned_text, term):
                numeric_weight = float(weight)
                category_scores[category] += numeric_weight
                matches_by_category[category].append(
                    (term, numeric_weight)
                )

    # Kategori ditentukan berdasarkan skor tertinggi.
    best_category = max(
        PROBLEM_LABEL_TO_ID,
        key=lambda category: (
            category_scores.get(category, 0.0),
            -PROBLEM_LABEL_TO_ID[category],
        ),
    )

    # Apabila tidak ada keyword yang cocok.
    if category_scores.get(best_category, 0.0) <= 0:
        best_category = "Masalah Lain"

    matched_pairs = sorted(
        matches_by_category.get(best_category, []),
        key=lambda item: (-item[1], item[0]),
    )

    matched_keywords = [
        term
        for term, _weight in matched_pairs
    ]

    recommended_feature = PROBLEM_TO_FEATURE[best_category]
    urgency = FEATURE_TO_URGENCY[recommended_feature]

    weighted_scores = {
        category: round(float(score), 6)
        for category, score in category_scores.items()
    }
    probabilities = _weighted_scores_to_probabilities(
        weighted_scores,
        fallback_label=best_category,
    )

    return {
        "kategori_masalah": best_category,
        "fitur": recommended_feature,
        "respon": RESPONSE_BY_PROBLEM[best_category],
        "skor_urgensi": urgency,
        "crisis_flag": "NO",
        "matched_keywords": matched_keywords,
        "weighted_scores": weighted_scores,
        "probabilities": probabilities,
    }


def get_default_assistant_message():
    return {
        "role": "assistant",
        "content": (
            "Halo, saya Audore Assistant. Silakan ceritakan keluhan "
            "atau pertanyaan Anda."
        ),
    }


def build_chat_title(messages):
    for message in messages:
        if message.get("role") == "user":
            title = message.get("content", "").strip()
            if len(title) > 42:
                title = title[:42].rstrip() + "..."
            return title

    return "Chat baru"



def get_max_chat_counter_from_sessions(sessions):
    max_counter = 1

    for session in sessions:
        session_id = str(session.get("id", ""))
        if session_id.startswith("chat_"):
            try:
                max_counter = max(max_counter, int(session_id.split("_", 1)[1]))
            except Exception:
                pass

    return max_counter

def initialize_chat_sessions():
    user_name = st.session_state.get("user_name", "Pengguna")

    if "assistant_chat_counter" not in st.session_state:
        st.session_state.assistant_chat_counter = 1

    if "assistant_chat_sessions" not in st.session_state:
        saved_sessions = load_chat_sessions(user_name)

        if saved_sessions:
            st.session_state.assistant_chat_sessions = saved_sessions
            st.session_state.assistant_chat_counter = get_max_chat_counter_from_sessions(saved_sessions)
        else:
            existing_messages = st.session_state.get("messages")

            if existing_messages:
                initial_messages = existing_messages
            else:
                initial_messages = [get_default_assistant_message()]

            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            st.session_state.assistant_chat_sessions = [
                {
                    "id": "chat_1",
                    "title": build_chat_title(initial_messages),
                    "messages": initial_messages,
                    "created_at": now,
                    "updated_at": now,
                }
            ]

    if "active_assistant_chat_id" not in st.session_state:
        st.session_state.active_assistant_chat_id = (
            st.session_state.assistant_chat_sessions[0]["id"]
        )


def get_current_chat_session():
    initialize_chat_sessions()

    for session in st.session_state.assistant_chat_sessions:
        if session["id"] == st.session_state.active_assistant_chat_id:
            return session

    st.session_state.active_assistant_chat_id = (
        st.session_state.assistant_chat_sessions[0]["id"]
    )
    return st.session_state.assistant_chat_sessions[0]


def update_current_chat_session(messages):
    current_session = get_current_chat_session()
    current_session["messages"] = messages
    current_session["title"] = build_chat_title(messages)
    current_session["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.messages = messages


def create_new_chat_session():
    st.session_state.assistant_chat_counter += 1
    chat_id = f"chat_{st.session_state.assistant_chat_counter}"
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    new_session = {
        "id": chat_id,
        "title": "Chat baru",
        "messages": [get_default_assistant_message()],
        "created_at": now,
        "updated_at": now,
    }

    st.session_state.assistant_chat_sessions.insert(0, new_session)
    st.session_state.active_assistant_chat_id = chat_id
    st.session_state.messages = new_session["messages"]


def clear_all_chat_sessions():
    user_name = st.session_state.get("user_name", "Pengguna")
    delete_chat_history(user_name)

    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.assistant_chat_counter = 1
    st.session_state.assistant_chat_sessions = [
        {
            "id": "chat_1",
            "title": "Chat baru",
            "messages": [get_default_assistant_message()],
            "created_at": now,
            "updated_at": now,
        }
    ]
    st.session_state.active_assistant_chat_id = "chat_1"
    st.session_state.messages = st.session_state.assistant_chat_sessions[0]["messages"]


def get_feature_page_from_prediction(prediction_label):
    """Map prediction label to an application page when navigation is appropriate."""
    prediction_label = (prediction_label or "").lower()

    if "darurat" in prediction_label or "krisis" in prediction_label:
        return None

    if "kebutuhan informasi" in prediction_label or "edukasi" in prediction_label:
        return "Edukasi"

    if prediction_label.strip() == "dukungan" or "komunitas" in prediction_label:
        return "Komunitas"

    return "Konsultasi"


def get_followup_content(feature_page, prediction_label=None):
    """Return contextual content shown after chatbot response."""
    prediction_label = prediction_label or feature_page
    prediction_label_lower = (prediction_label or "").lower()

    # Kasus darurat tidak diarahkan ke halaman pembuatan janji konsultasi.
    if "darurat" in prediction_label_lower or "krisis" in prediction_label_lower:
        return {
            "badge": "Bantuan Darurat",
            "title": "Segera cari bantuan langsung",
            "description": (
                "Keluhan ini memerlukan bantuan segera. Jangan menunggu jadwal "
                "konsultasi di aplikasi dan jangan menghadapi kondisi ini sendirian."
            ),
            "items": [
                "Hubungi orang terdekat yang dapat segera datang dan mendampingi Anda.",
                "Jauhkan benda, obat, atau alat yang dapat digunakan untuk menyakiti diri.",
                "Datangi IGD atau fasilitas kesehatan terdekat, atau hubungi layanan darurat setempat.",
            ],
            "button": None,
            "target_page": None,
            "note": (
                "Audore Assistant bukan layanan gawat darurat. Pada kondisi darurat, "
                "utamakan bantuan langsung dari orang terdekat dan tenaga kesehatan."
            ),
        }

    if feature_page == "Edukasi":
        return {
            "badge": "Artikel Edukasi Terkait",
            "title": "Memahami kebutuhan anak ASD saat caregiver merasa bingung",
            "description": (
                "Bagian ini mengarahkan caregiver ke materi edukasi yang relevan "
                "agar informasi mengenai ASD, terapi, pendidikan, dan strategi "
                "pengasuhan dapat dibaca secara lebih terstruktur."
            ),
            "items": [
                "Kenali pola perilaku anak yang sering muncul di rumah.",
                "Catat pemicu, respons anak, dan strategi yang cukup membantu.",
                "Gunakan materi edukasi singkat agar informasi lebih mudah diterapkan.",
            ],
            "button": "Buka Artikel Edukasi",
            "note": "Rekomendasi ini ditampilkan ketika keluhan lebih berkaitan dengan kebutuhan informasi.",
        }

    if feature_page == "Komunitas":
        return {
            "badge": "Topik Komunitas Terkait",
            "title": "Berbagi pengalaman dengan caregiver lain",
            "description": (
                "Bagian ini mengarahkan caregiver ke ruang komunitas untuk melihat "
                "pengalaman, dukungan sebaya, dan strategi dari caregiver lain "
                "yang menghadapi situasi serupa."
            ),
            "items": [
                "Diskusi: cara menghadapi rasa sendirian saat mendampingi anak.",
                "Cerita caregiver: membangun rutinitas harian yang lebih tenang.",
                "Dukungan sebaya: berbagi pengalaman tanpa menghakimi.",
            ],
            "button": "Buka Komunitas",
            "note": "Rekomendasi ini ditampilkan ketika keluhan menunjukkan kebutuhan dukungan sosial.",
        }

    if "pengasuhan" in prediction_label_lower:
        return {
            "badge": "Lanjutan Konsultasi",
            "title": "Siapkan poin konsultasi sebelum berdiskusi",
            "description": (
                "Bagian ini membantu caregiver merapikan keluhan pengasuhan "
                "sebelum menggunakan fitur Konsultasi, sehingga diskusi dengan "
                "tenaga profesional menjadi lebih terarah."
            ),
            "items": [
                "Keluhan utama: rasa lelah, stres, atau kewalahan.",
                "Situasi pemicu: kapan keluhan paling sering muncul.",
                "Harapan konsultasi: strategi pengelolaan stres dan dukungan pengasuhan.",
            ],
            "button": "Lanjut ke Konsultasi",
            "note": "Rekomendasi ini ditampilkan ketika keluhan berkaitan dengan tekanan pengasuhan.",
        }

    return {
        "badge": "Lanjutan Konsultasi",
        "title": "Rencana konsultasi awal",
        "description": (
            "Bagian ini membantu caregiver memahami langkah berikutnya setelah "
            "Audore Assistant merekomendasikan fitur Konsultasi."
        ),
        "items": [
            "Tuliskan keluhan utama yang ingin dibahas.",
            "Siapkan contoh kejadian yang paling menggambarkan masalah.",
            "Pilih jadwal konsultasi yang tersedia di fitur Konsultasi.",
        ],
        "button": "Buka Konsultasi",
        "note": "Rekomendasi ini ditampilkan ketika keluhan membutuhkan arahan konsultasi lanjutan.",
    }


def open_feature_page(page_name):
    st.session_state.active_page = page_name
    st.rerun()

def render_crisis_actions():
    """Menampilkan akses langsung ke layanan darurat."""

    st.error(
        """
        **Bantuan Darurat**

        Kondisi yang disampaikan memerlukan bantuan segera. Jangan menunggu
        jadwal konsultasi. Hubungi layanan darurat, minta pendampingan orang
        terdekat, atau datangi IGD terdekat.
        """
    )

    col1, col2 = st.columns(2, gap="small")

    with col1:
        # Tautan telepon tidak dibuka sebagai tab baru. Pada ponsel, tautan ini
        # akan membuka aplikasi Telepon. Pada laptop, keberhasilannya bergantung
        # pada aplikasi yang menangani protokol tel:.
        st.markdown(
            """
            <a href="tel:119" style="
                display: block;
                width: 100%;
                box-sizing: border-box;
                padding: 0.68rem 1rem;
                background: #FF4B4B;
                color: #FFFFFF;
                text-align: center;
                text-decoration: none;
                border-radius: 999px;
                font-weight: 700;
                line-height: 1.25;
                box-shadow: 0 10px 22px rgba(255, 75, 75, 0.18);
            ">
                Hubungi PSC 119 Sekarang
            </a>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.link_button(
            "Cari IGD Terdekat",
            url="https://www.google.com/maps/search/?api=1&query=IGD+terdekat",
            use_container_width=True,
        )

    st.info(
        "Jika tombol panggilan tidak berfungsi pada laptop, hubungi **119** "
        "melalui telepon seluler."
    )

    st.caption(
        "Audore Assistant memberikan arahan awal dan bukan pengganti "
        "penanganan langsung oleh tenaga kesehatan."
    )


def render_followup_content(message, message_index):
    """Render extra content after chatbot response and model analysis."""
    prediction_label = message.get("prediction_label", "")

    if not prediction_label:
        return

    crisis_flag = str(message.get("crisis_flag", "NO")).upper()

    # Kondisi krisis langsung menampilkan akses bantuan nyata.
    if crisis_flag == "YES":
        render_crisis_actions()
        st.write("")
        return

    feature_page = message.get("recommended_feature")

    if feature_page in {"Edukasi", "Komunitas", "Konsultasi"}:
        navigation_page = feature_page
    else:
        navigation_page = get_feature_page_from_prediction(prediction_label)

    followup = get_followup_content(feature_page, prediction_label)

    safe_badge = html.escape(followup.get("badge", "Rekomendasi Lanjutan"))
    safe_title = html.escape(followup.get("title", "Lanjutan fitur Audore"))
    safe_description = html.escape(followup.get("description", ""))
    safe_note = html.escape(followup.get("note", ""))

    item_html = ""
    for item in followup.get("items", []):
        item_html += f"<li>{html.escape(item)}</li>"

    st.markdown(
        f"""
        <div class="followup-card">
            <div class="followup-badge">{safe_badge}</div>
            <h4>{safe_title}</h4>
            <p>{safe_description}</p>
            <ul>{item_html}</ul>
            <div class="followup-note">{safe_note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    button_label = followup.get("button")
    target_page = followup.get("target_page", navigation_page)

    # Tombol navigasi hanya ditampilkan untuk rekomendasi non-darurat.
    if button_label and target_page:
        button_col, spacer_col = st.columns([1.15, 2.85], gap="small")
        with button_col:
            if st.button(
                button_label,
                key=f"open_followup_{message_index}_{target_page}",
                use_container_width=True,
            ):
                open_feature_page(target_page)

    st.write("")



def _extract_message_probabilities(message):
    """
    Ambil probabilitas yang berasal dari normalisasi weighted scoring.

    Riwayat lama tetap didukung. Jika weighted_scores tersedia, nilai
    probabilitas lama dari SVC diabaikan dan dihitung ulang dari skor bobot.
    """
    fallback_label = message.get("prediction_label")

    weighted_scores = message.get("weighted_scores")
    if isinstance(weighted_scores, dict):
        return _weighted_scores_to_probabilities(
            weighted_scores,
            fallback_label=fallback_label,
        )

    stored_scores = message.get("scores")
    if isinstance(stored_scores, dict):
        nested_weighted_scores = stored_scores.get("weighted_scores")
        if isinstance(nested_weighted_scores, dict):
            return _weighted_scores_to_probabilities(
                nested_weighted_scores,
                fallback_label=fallback_label,
            )

    # Kompatibilitas untuk riwayat yang benar-benar belum memiliki
    # weighted_scores.
    probabilities = message.get("probabilities")
    if isinstance(probabilities, dict):
        return probabilities

    if isinstance(stored_scores, dict):
        nested_probabilities = stored_scores.get("probabilities")
        if isinstance(nested_probabilities, dict):
            return nested_probabilities

        if any(label in stored_scores for label in PROBABILITY_LABELS):
            return stored_scores

    return {}


def _render_probability_rows(probabilities, probability_labels):
    rows = ["<div class='model-meta'><b>Probabilitas hasil weighted scoring</b></div>"]
    for label in probability_labels:
        try:
            probability = float(probabilities.get(label, 0.0))
        except (TypeError, ValueError):
            probability = 0.0

        probability = min(1.0, max(0.0, probability))
        percentage = probability * 100.0
        safe_label = html.escape(str(label))
        rows.append(
            "<div class='proba-row'>"
            "<div class='proba-label'>"
            f"<span>{safe_label}</span><span>{percentage:.1f}%</span>"
            "</div>"
            "<div class='proba-track'>"
            f"<div class='proba-fill' style='width:{percentage:.4f}%'></div>"
            "</div>"
            "</div>"
        )

    return "".join(rows)


def render_message(message, user_initial, probability_labels, message_index):
    content_html = html.escape(message["content"]).replace("\n", "<br>")

    if message["role"] == "user":
        st.markdown(
            f"""
            <div class="chat-row user">
                <div class="chat-bubble user">{content_html}</div>
                <div class="chat-avatar user">{user_initial}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"""
        <div class="chat-row assistant">
            <div class="chat-avatar assistant">A</div>
            <div class="chat-bubble assistant">{content_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "prediction_label" not in message:
        return

    kategori_masalah = html.escape(str(message.get("prediction_label", "-")))
    recommended_feature = html.escape(str(message.get("recommended_feature", "-")))
    skor_urgensi = html.escape(str(message.get("skor_urgensi", "-")))
    crisis_flag = html.escape(str(message.get("crisis_flag", "NO")))

    matched_keywords = message.get("matched_keywords", [])
    if matched_keywords:
        matched_keywords_text = ", ".join(html.escape(str(item)) for item in matched_keywords)
    else:
        matched_keywords_text = "Tidak ada keyword dengan koefisien > 1 yang cocok"

    probabilities = _extract_message_probabilities(message)

    displayed_probability_labels = [
        label
        for label in probability_labels
        if label in probabilities
    ]
    displayed_probability_labels.extend(
        label
        for label in probabilities
        if label not in displayed_probability_labels
    )

    probability_html = _render_probability_rows(
        probabilities,
        displayed_probability_labels,
    )

    model_html = (
        "<div class='model-card'>"
        "<h4>Hasil Analisis Audore Assistant</h4>"
        "<div class='model-meta'>"
        f"Kategori masalah internal: <b>{kategori_masalah}</b><br>"
        f"Rekomendasi fitur: <b>{recommended_feature}</b><br>"
        f"Skor urgensi: <b>{skor_urgensi}/4</b><br>"
        f"Crisis flag: <b>{crisis_flag}</b><br>"
        f"Keyword cocok: <b>{matched_keywords_text}</b>"
        "</div>"
        f"{probability_html}"
        "</div>"
    )

    st.markdown(model_html, unsafe_allow_html=True)
    render_followup_content(message, message_index)



def run_ml_app():
    init_db()

    try:
        dataset_path = resolve_dataset_path()
        keyword_resources = initialize_keyword_resources(
            str(dataset_path.resolve()),
            dataset_path.stat().st_mtime_ns,
        )
    except Exception as exc:
        st.error("Model Audore belum dapat disiapkan.")
        st.code(str(exc), language=None)
        return

    st.markdown(
        """
        <style>
        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"] {
            color-scheme: light;
        }

        .assistant-page {
            max-width: 1040px;
            margin: 0 auto;
        }

        .assistant-toolbar {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(122, 90, 248, 0.10);
            border-radius: 20px;
            padding: 0.85rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 12px 28px rgba(88, 72, 124, 0.07);
        }

        .assistant-toolbar-title {
            color: #2F2A38;
            font-size: 0.95rem;
            font-weight: 800;
            margin: 0;
        }

        .assistant-toolbar-subtitle {
            color: #6A6278;
            font-size: 0.82rem;
            margin: 0.2rem 0 0 0;
        }

        .assistant-hero {
            background:
                radial-gradient(circle at top left, #FFDDE7 0%, transparent 38%),
                radial-gradient(circle at bottom right, #E9E1FF 0%, transparent 42%),
                linear-gradient(145deg, #FFFFFF 0%, #FFF9FA 100%);
            border: 1px solid rgba(122, 90, 248, 0.10);
            border-radius: 28px;
            box-shadow: 0 18px 42px rgba(88, 72, 124, 0.10);
            padding: 2.2rem 2.4rem;
            margin-bottom: 1.4rem;
        }

        .assistant-badge {
            display: inline-block;
            background: #FFDDE7;
            color: #3A2E3F;
            border-radius: 999px;
            padding: 0.45rem 0.85rem;
            font-size: 0.86rem;
            font-weight: 700;
            margin-bottom: 1.1rem;
        }

        .assistant-hero h1 {
            color: #111111;
            font-size: 2.25rem;
            font-weight: 800;
            margin: 0 0 0.65rem 0;
            letter-spacing: 0;
        }

        .assistant-hero p {
            color: #5F5870;
            font-size: 1.05rem;
            line-height: 1.7;
            margin: 0;
        }

        .assistant-info-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(122, 90, 248, 0.10);
            border-radius: 22px;
            padding: 1.1rem 1.25rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 14px 34px rgba(88, 72, 124, 0.08);
        }

        .assistant-info-card h3 {
            color: #2F2A38;
            font-size: 1.05rem;
            font-weight: 800;
            margin: 0 0 0.35rem 0;
        }

        .assistant-info-card p {
            color: #4F485D;
            font-size: 0.95rem;
            line-height: 1.6;
            margin: 0;
        }

        .history-item {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(122, 90, 248, 0.10);
            border-radius: 16px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.75rem;
        }

        .history-title {
            color: #2F2A38;
            font-size: 0.92rem;
            font-weight: 800;
            margin: 0;
        }

        .history-meta {
            color: #7A728A;
            font-size: 0.78rem;
            margin-top: 0.15rem;
        }

        .chat-row {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            margin-bottom: 1rem;
            width: 100%;
        }

        .chat-row.user {
            justify-content: flex-end;
        }

        .chat-row.assistant {
            justify-content: flex-start;
        }

        .chat-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-size: 0.82rem;
            font-weight: 800;
        }

        .chat-avatar.assistant {
            background: #FFDDE7;
            color: #3A2E3F;
        }

        .chat-avatar.user {
            background: #E9E1FF;
            color: #3A2E3F;
        }

        .chat-bubble {
            max-width: 68%;
            padding: 0.95rem 1.05rem;
            border-radius: 20px;
            font-size: 0.98rem;
            line-height: 1.65;
            word-break: break-word;
            white-space: pre-wrap;
            box-shadow: 0 12px 28px rgba(88, 72, 124, 0.07);
        }

        .chat-bubble.assistant {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(122, 90, 248, 0.10);
            color: #2F2A38;
            border-top-left-radius: 8px;
        }

        .chat-bubble.user {
            background: #FFF0C9;
            border: 1px solid rgba(255, 210, 110, 0.35);
            color: #2F2A38;
            border-top-right-radius: 8px;
        }

        .model-card {
            max-width: 68%;
            margin: -0.35rem 0 1.2rem 3rem;
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(122, 90, 248, 0.12);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 12px 28px rgba(88, 72, 124, 0.07);
        }

        .model-card h4 {
            margin: 0 0 0.7rem 0;
            color: #2F2A38;
            font-size: 0.95rem;
            font-weight: 800;
        }

        .model-meta {
            color: #5F5870;
            font-size: 0.82rem;
            line-height: 1.5;
            margin-bottom: 0.7rem;
        }

        .proba-row {
            margin-bottom: 0.55rem;
        }

        .proba-label {
            display: flex;
            justify-content: space-between;
            color: #3A3442;
            font-size: 0.82rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .proba-track {
            height: 8px;
            background: #F1EDF8;
            border-radius: 999px;
            overflow: hidden;
        }

        .proba-fill {
            height: 100%;
            background: linear-gradient(90deg, #FFDDE7, #E9E1FF);
            border-radius: 999px;
        }

        .followup-card {
            max-width: 68%;
            margin: -0.25rem 0 0.75rem 3rem;
            background:
                radial-gradient(circle at top left, rgba(255, 221, 231, 0.72) 0%, transparent 42%),
                radial-gradient(circle at bottom right, rgba(234, 246, 255, 0.88) 0%, transparent 48%),
                linear-gradient(145deg, #FFFFFF 0%, #FFF9FA 100%);
            border: 1px solid rgba(122, 90, 248, 0.12);
            border-radius: 20px;
            padding: 1rem 1.05rem;
            box-shadow: 0 12px 28px rgba(88, 72, 124, 0.07);
        }

        .followup-badge {
            display: inline-block;
            background: rgba(233, 225, 255, 0.95);
            color: #3A2E3F;
            border-radius: 999px;
            padding: 0.35rem 0.7rem;
            font-size: 0.76rem;
            font-weight: 800;
            margin-bottom: 0.65rem;
        }

        .followup-card h4 {
            margin: 0 0 0.45rem 0;
            color: #2F2A38;
            font-size: 1rem;
            font-weight: 800;
        }

        .followup-card p {
            margin: 0 0 0.65rem 0;
            color: #4F485D;
            font-size: 0.88rem;
            line-height: 1.55;
        }

        .followup-card ul {
            margin: 0.15rem 0 0.75rem 1.05rem;
            padding: 0;
            color: #4F485D;
            font-size: 0.84rem;
            line-height: 1.55;
        }

        .followup-note {
            color: #6A6278;
            font-size: 0.78rem;
            line-height: 1.45;
            background: rgba(255, 255, 255, 0.64);
            border-radius: 12px;
            padding: 0.55rem 0.65rem;
        }

        label,
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] p,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p {
            color: #2F2A38 !important;
        }

        div[data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.86) !important;
            border: 1px solid rgba(122, 90, 248, 0.10) !important;
            border-radius: 18px !important;
            color: #2F2A38 !important;
        }

        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] summary p {
            color: #2F2A38 !important;
            font-weight: 800 !important;
        }

        div[data-testid="stChatInput"] {
            max-width: 1040px;
            margin: 0 auto;
            background: transparent !important;
        }

        div[data-testid="stChatInput"] > div {
            background: rgba(255, 255, 255, 0.96) !important;
            border: 1px solid rgba(122, 90, 248, 0.16) !important;
            border-radius: 18px !important;
            box-shadow: 0 14px 34px rgba(88, 72, 124, 0.10) !important;
        }

        div[data-testid="stChatInput"] textarea {
            background: rgba(255, 255, 255, 0.96) !important;
            color: #2F2A38 !important;
            caret-color: #2F2A38 !important;
            border-radius: 18px !important;
            border: 0 !important;
        }

        div[data-testid="stChatInput"] textarea::placeholder {
            color: #8A819A !important;
            opacity: 1 !important;
        }

        div[data-testid="stChatInput"] button {
            background: #F3F0FF !important;
            color: #2F2A38 !important;
            border-radius: 14px !important;
        }

        div[data-testid="stButton"] > button {
            border-radius: 999px;
            font-weight: 700;
            min-height: 2.55rem;
            background: rgba(255, 255, 255, 0.92) !important;
            color: #514568 !important;
            border: 1px solid rgba(122, 90, 248, 0.18) !important;
            box-shadow: 0 10px 22px rgba(122, 90, 248, 0.10);
        }

        div[data-testid="stButton"] > button:hover {
            background: #F8FBFF !important;
            color: #2F2A38 !important;
            border-color: rgba(122, 90, 248, 0.28) !important;
        }

        @media (max-width: 768px) {
            .assistant-hero {
                padding: 1.5rem;
            }

            .assistant-hero h1 {
                font-size: 1.85rem;
            }

            .chat-bubble,
            .model-card,
            .followup-card {
                max-width: 82%;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    initialize_chat_sessions()
    current_session = get_current_chat_session()
    messages = current_session["messages"]

    st.markdown('<div class="assistant-page">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="assistant-toolbar">
            <p class="assistant-toolbar-title">Audore Assistant</p>
            <p class="assistant-toolbar-subtitle">
                Kelola percakapan, buka riwayat, atau kembali ke halaman utama.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    back_col, new_chat_col, empty_col = st.columns([1, 1, 3], gap="small")

    with back_col:
        if st.button("Kembali", use_container_width=True):
            st.session_state.active_page = "Home"
            st.rerun()

    with new_chat_col:
        if st.button("Chat Baru", use_container_width=True):
            create_new_chat_session()
            st.rerun()

    with st.expander("Riwayat Chat", expanded=False):
        if not st.session_state.assistant_chat_sessions:
            st.info("Belum ada riwayat chat.")
        else:
            for session in st.session_state.assistant_chat_sessions:
                is_active = session["id"] == st.session_state.active_assistant_chat_id
                active_label = "Aktif" if is_active else "Buka"
                safe_title = html.escape(session["title"])
                safe_time = html.escape(session["updated_at"])

                st.markdown(
                    f"""
                    <div class="history-item">
                        <p class="history-title">{safe_title}</p>
                        <div class="history-meta">Terakhir diperbarui: {safe_time}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    active_label,
                    key=f"open_history_{session['id']}",
                    use_container_width=True,
                    disabled=is_active,
                ):
                    st.session_state.active_assistant_chat_id = session["id"]
                    st.session_state.messages = session["messages"]
                    st.rerun()

        if st.button("Hapus Semua Riwayat", use_container_width=True):
            clear_all_chat_sessions()
            st.rerun()

    st.markdown(
        """
        <div class="assistant-hero">
            <div class="assistant-badge">Audore Assistant</div>
            <h1>Audore Assistant</h1>
            <p>
                Ceritakan keluhan atau pengalaman Anda mengenai pengasuhan,
                terapi, pendidikan, maupun kondisi psikologis terkait Autism
                Spectrum Disorder.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    probability_labels = PROBABILITY_LABELS

    user_name = st.session_state.get("user_name", "Pengguna")
    user_initial = user_name[:1].upper() if user_name else "U"

    for index, message in enumerate(messages):
        render_message(message, user_initial, probability_labels, index)

    st.markdown("</div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Ketikkan keluhan Anda"):
        user_name = st.session_state.get("user_name", "Pengguna")
        current_session = get_current_chat_session()
        session_id = current_session["id"]

        user_message = {
            "role": "user",
            "content": prompt,
        }
        messages.append(user_message)

        save_chat_message(
            user_name=user_name,
            session_id=session_id,
            session_title=build_chat_title(messages),
            role="user",
            content=prompt,
        )

        clean_prompt = clean(prompt)

        try:
            hasil_model = classify_keluhan_weighted(prompt, keyword_resources)

            assistant_message = {
                "role": "assistant",
                "content": hasil_model["respon"],
                "prediction_label": hasil_model["kategori_masalah"],
                "recommended_feature": hasil_model["fitur"],
                "matched_keywords": hasil_model["matched_keywords"],
                "skor_urgensi": hasil_model["skor_urgensi"],
                "crisis_flag": hasil_model["crisis_flag"],
                "weighted_scores": hasil_model["weighted_scores"],
                "probabilities": hasil_model["probabilities"],
            }
            messages.append(assistant_message)

            save_chat_message(
                user_name=user_name,
                session_id=session_id,
                session_title=build_chat_title(messages),
                role="assistant",
                content=hasil_model["respon"],
                clean_text=clean_prompt,
                kategori_output=hasil_model["kategori_masalah"],
                kategori_masalah=hasil_model["kategori_masalah"],
                recommended_feature=hasil_model["fitur"],
                matched_keywords=hasil_model["matched_keywords"],
                skor_urgensi=hasil_model["skor_urgensi"],
                crisis_flag=hasil_model["crisis_flag"],
                scores={
                    "weighted_scores": hasil_model["weighted_scores"],
                    "probabilities": hasil_model["probabilities"],
                },
            )

        except Exception as exc:
            st.error(f"Proses klasifikasi gagal: {exc}")
            error_message = (
                "Maaf, keluhan Anda belum dapat diproses oleh sistem. "
                "Silakan tuliskan kembali keluhan dengan kalimat yang lebih jelas, "
                "atau gunakan fitur Konsultasi untuk memperoleh arahan lebih lanjut."
            )

            messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )

            save_chat_message(
                user_name=user_name,
                session_id=session_id,
                session_title=build_chat_title(messages),
                role="assistant",
                content=error_message,
            )

        update_current_chat_session(messages)
        st.rerun()