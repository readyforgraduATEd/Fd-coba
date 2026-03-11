# ============================================

# PROYEK FLASHCARD DIGITAL - INFORMATIKA

# NAMA: [ISI NAMA LENGKAP KAMU]

# KELAS: [ISI KELAS]

# TANGGAL: MARET 2026

# ============================================



import streamlit as st

import pandas as pd

import gspread

from google.oauth2.service_account import Credentials

import random

from datetime import datetime



# ============================================

# SETUP HALAMAN

# ============================================

st.set_page_config(

    page_title="Flashcard Digital",

    page_icon="??",

    layout="centered"

)



# ============================================

# KONEKSI KE GOOGLE SHEETS (bagian tersulit -_-, 

# tapi alhamdulillah akhirnya bisa setelah baca dan lihat tutorial)

# ============================================

@st.cache_resource

def get_google_sheet():

    """Koneksi ke Google Sheets"""

    try:

        # ini scope nya buat akses spreadsheet dan drive

        scope = ["https://www.googleapis.com/auth/spreadsheets", 

                 "https://www.googleapis.com/auth/drive"]

        

        # ambil dari secrets (nanti diatur di streamlit cloud)

        creds = Credentials.from_service_account_info(

            st.secrets["gcp_service_account"], 

            scopes=scope

        )

        client = gspread.authorize(creds)

        

        # GANTI PAKAI ID SPREADSHEET KAMU YA!

        # caranya: buka google sheets, lihat url nya, 

        # ambil yg panjang itu (contoh: 1abcDEFghijk...)

        SHEET_ID = "1KnzVTCWVnLsTI6zie3x1_ivj7Vo-50TN"  # <-- GANTI INI!

        

        sh = client.open_by_key(SHEET_ID)

        return sh

    except Exception as e:

        # kalo error kasih tau user

        st.error(f"Gagal konek ke Google Sheets: {e}")

        return None



# ============================================

# FUNGSI AMBIL DATA SOAL DARI SHEET

# ============================================

@st.cache_data(ttl=600)  # cache 10 menit biar ga lemot

def get_data():

    sh = get_google_sheet()

    if sh:

        # ambil sheet yg namanya "kosakata"

        sheet_soal = sh.worksheet("kosakata")

        # convert ke dataframe pandas

        return pd.DataFrame(sheet_soal.get_all_records())

    return pd.DataFrame()



# ============================================

# FUNGSI NYIMPEN HASIL BELAJAR

# ============================================

def save_log(nama, topik, skor, total, salah):

    sh = get_google_sheet()

    if sh:

        try:

            # coba ambil sheet log

            sheet_log = sh.worksheet("Log_Belajar_Flashcard")

            

            # format waktu sekarang

            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            

            # ubah list salah jadi string biar bisa disimpan

            if salah:

                salah_str = ", ".join(salah)

            else:

                salah_str = "? Sempurna!"

            

            # simpan baris baru

            sheet_log.append_row([waktu, nama, topik, skor, total, salah_str])

            return True

        except:

            # kalo sheet log belum ada, buat baru dulu

            sheet_log = sh.add_worksheet(title="Log_Belajar_Flashcard", rows=1000, cols=6)

            sheet_log.append_row(["Waktu", "Nama", "Topik", "Skor", "Total Soal", "Kata Salah"])

            sheet_log.append_row([waktu, nama, topik, skor, total, salah_str])

            return True

    return False



# ============================================

# MULAI TAMPILAN WEB

# ============================================

st.title("?? Digital Flashcard")

st.markdown("### Uji kemampuan kosakata bahasa Inggrismu!")



# ============================================

# INI BUAT NYIMPEN DATA SEMENTARA

# (biar ga ilang kalo page di refresh)

# ============================================

if 'quiz_started' not in st.session_state:

    st.session_state.quiz_started = False



# ============================================

# SIDEBAR (bagian samping kiri)

# ============================================

with st.sidebar:

    st.header("?? Info")

    st.write("""

    **Cara pakai:**

    1. Masukkan nama

    2. Pilih kategori

    3. Jawab 5 soal

    4. Lihat skor akhir

    

    **Topik tersedia:**

    - Phrasal Verbs

    - Academic Words



    """)

    

    # tombol reset kalo mau mulai dari awal

    if st.button("?? Reset Aplikasi"):

        st.session_state.quiz_started = False

        st.rerun()



# ============================================

# BAGIAN UTAMA (HALAMAN AWAL)

# ============================================

if not st.session_state.quiz_started:

    # bikin 2 kolom biar rapi

    col1, col2 = st.columns(2)

    

    # kolom 1 buat input nama

    with col1:

        nama = st.text_input("?? Masukkan Namamu:", placeholder="Contoh: Setiawan")

    

    # ambil data dari google sheets

    df = get_data()

    

    # kalo data kosong kasih warning

    if df.empty:

        st.warning("?? Data kosakata belum tersedia. Hubungi admin.")

        st.stop()

    

    # ambil daftar topik unik buat ditampilin di combobox

    topik_list = df['topik'].unique()

    

    # kolom 2 buat pilih topik

    with col2:

        topik = st.selectbox("?? Pilih Kategori:", topik_list)

    

    # tampilin jumlah soal yg tersedia di topik ini

    jumlah_soal = len(df[df['topik'] == topik])

    st.info(f"?? Tersedia **{jumlah_soal}** kosakata di kategori ini")

    

    # tombol mulai kuis

    if st.button("?? Mulai Kuis", type="primary"):

        # validasi nama harus diisi

        if nama.strip() == "":

            st.error("Isi namamu dulu ya!")

        else:

            # ambil 5 soal acak dari topik yg dipilih

            df_filter = df[df['topik'] == topik].sample(n=min(5, jumlah_soal))

            

            # simpan ke session state

            st.session_state.questions = df_filter.to_dict('records')

            st.session_state.nama = nama

            st.session_state.topik = topik

            st.session_state.answers = {}

            st.session_state.quiz_started = True

            

            # refresh halaman

            st.rerun()



# ============================================

# BAGIAN KUIS (SETELAH MULAI)

# ============================================

else:

    # tampilkan info

    st.subheader(f"?? Kategori: **{st.session_state.topik}**")

    st.caption(f"Selamat mengerjakan, {st.session_state.nama}!")

    

    # progress bar (hiasan doang biar keren)

    progress = len(st.session_state.answers) / len(st.session_state.questions)

    st.progress(progress)

    

    # form buat jawaban

    with st.form("quiz_form"):

        # loop buat tiap soal

        for i, q in enumerate(st.session_state.questions):

            with st.container():

                st.markdown(f"**Soal {i+1}:** Apa arti dari kata")

                st.markdown(f"# {q['kata'].upper()}")

                

                # kalo ada contoh kalimat, tampilkan

                if pd.notna(q.get('contoh_kalimat')) and q['contoh_kalimat']:

                    st.caption(f"?? Contoh: _{q['contoh_kalimat']}_")

                

                # input jawaban

                st.session_state.answers[i] = st.text_input(

                    f"Jawaban No {i+1}", 

                    key=f"q{i}",

                    placeholder="Ketik artinya dalam Bahasa Indonesia..."

                ).strip().lower()

                st.divider()

        

        # tombol2

        col1, col2 = st.columns(2)

        with col1:

            submitted = st.form_submit_button("? Kirim Jawaban", type="primary", use_container_width=True)

        with col2:

            batal = st.form_submit_button("?? Batalkan", use_container_width=True)

        

        # ============================================

        # PROSES KALAU TOMBOL KIRIM DI KLIK

        # ============================================

        if submitted:

            # cek apakah semua jawaban diisi

            semua_isi = True

            for v in st.session_state.answers.values():

                if v == "":

                    semua_isi = False

                    break

            

            if not semua_isi:

                st.warning("?? Ada jawaban yang kosong! Isi semua dulu ya.")

            else:

                # koreksi jawaban

                skor = 0

                salah_list = []

                

                for i, q in enumerate(st.session_state.questions):

                    jawaban_user = st.session_state.answers[i]

                    jawaban_benar = str(q['arti']).lower().strip()

                    

                    # kalo jawaban benar pake tanda / (misal: rusak/analisis)

                    if '/' in jawaban_benar:

                        # pisahin berdasarkan /

                        options = jawaban_benar.split('/')

                        # bersihin spasi

                        clean_options = []

                        for opt in options:

                            clean_options.append(opt.strip())

                        

                        # cek apakah jawaban user ada di salah satu opsi

                        if jawaban_user in clean_options:

                            skor += 1

                        else:

                            salah_list.append(f"{q['kata']} (jawaban: {jawaban_benar})")

                    else:

                        # kalo jawaban cuma satu

                        if jawaban_user == jawaban_benar:

                            skor += 1

                        else:

                            salah_list.append(f"{q['kata']} (benar: {q['arti']})")

                

                # simpan ke google sheets

                tersimpan = save_log(

                    st.session_state.nama, 

                    st.session_state.topik, 

                    skor, 

                    len(st.session_state.questions), 

                    salah_list

                )

                

                # tampilkan hasil

                st.balloons()

                st.success(f"### ? Selesai! Skor kamu: **{skor}/{len(st.session_state.questions)}**")

                

                # tampilkan pembahasan kalo ada yg salah

                if salah_list:

                    with st.expander("?? PEMBAHASAN (Kata yang salah)"):

                        for item in salah_list:

                            st.write(f"- {item}")

                else:

                    st.info("?? SELAMAT! Kamu menjawab semua dengan benar!")

                

                if tersimpan:

                    st.caption("?? Hasil belajarmu sudah tercatat! Thanks for your participate")

                

                # tombol buat main lagi

                if st.button("?? Kerjakan Lagi", use_container_width=True):

                    st.session_state.quiz_started = False

                    st.rerun()

        

        # ============================================

        # KALAU TOMBOL BATAL DI KLIK

        # ============================================

        if batal:

            st.session_state.quiz_started = False

            st.rerun()
