
import streamlit as st

st.set_page_config(page_title="Kalkulator NKP KMK 127/2026", layout="wide")

# --- HEADER & DISCLAIMER ---
st.title("📊 Kalkulator Estimasi NKP — UPK")
st.caption("Berdasarkan Lampiran II, Keputusan Menteri Keuangan Nomor 127 Tahun 2026")
st.warning("⚠️ **Catatan Penting:** Alat bantu edukatif, bukan pengganti sistem e-performance resmi.")

# --- SIDEBAR: KOMPONEN UTAMA ---
st.sidebar.header("🎛️ Komponen Lain")
npk_awal = st.sidebar.number_input("NPK Awal (Nilai Perilaku)", min_value=0.0, max_value=150.0, value=95.0)
nko_unit = st.sidebar.number_input("NKO Unit Kerja", min_value=0.0, max_value=150.0, value=100.0)
nilai_koreksi = st.sidebar.number_input("Nilai Koreksi (Bisa Negatif)", value=0.0)
hukdis = st.sidebar.number_input("Nilai Hukuman Disiplin", min_value=0.0, value=0.0)
dampak_disiplin = st.sidebar.number_input("Nilai Dampak Pelanggaran Disiplin", min_value=0.0, value=0.0)

posisi = st.sidebar.selectbox(
    "Posisi Terhadap Pimpinan UPK",
    ["2 tingkat atau lebih di bawah Pimpinan UPK (termasuk Pelaksana)", "1 tingkat di bawah Pimpinan UPK", "Pimpinan UPK"]
)

# --- TABS UNTUK INPUT IKI ---
st.header("📝 Input IKI pada SKP")

# Simulasi untuk 1 Baris IKI terlebih dahulu (bisa dilooping jika ingin banyak)
col1, col2, col3, col4 = st.columns(4)

with col1:
    nama_iki = st.text_input("Nama IKI", value="Persentase penyelesaian layanan tepat waktu")
    polaritas = st.selectbox("Polaritas", ["Maximize", "Minimize"])

with col2:
    validitas = st.selectbox("Validitas", ["Exact", "Proxy", "Activity"])
    kendali = st.selectbox("Kendali", ["Low", "Moderate", "High"])

with col3:
    iki_baru = st.checkbox("IKI Baru tanpa historis?")
    target_lalu = st.number_input("Target Th Lalu", min_value=0.0, value=90.0, disabled=iki_baru)
    realisasi_lalu = st.number_input("Realisasi Th Lalu", min_value=0.0, value=92.0, disabled=iki_baru)

with col4:
    target_ini = st.number_input("Target Th Ini", min_value=0.0, value=93.0)
    realisasi_ini = st.number_input("Realisasi Th Ini", min_value=0.0, value=95.0)
    
    # VALIDASI OTOMATIS 1: Kondisional Kolom Realisasi Terburuk
    realisasi_terburuk = None
    if polaritas == "Minimize" and target_ini == 0:
        realisasi_terburuk = st.number_input("⚠️ Realisasi Terburuk (Ambang Toleransi)", min_value=0.1, value=10.0)

# --- PROSES VALIDASI OTOMATIS SEBELUM HITUNG ---
st.divider()
st.header("🔍 Validasi & Hasil Perhitungan")

valid_to_calculate = True

# VALIDASI OTOMATIS 2: Blokir Kombinasi Terlarang Tabel 14
if (validitas == "Exact" and kendali == "High") or (validitas == "Activity" and kendali == "Low"):
    st.error(f"❌ **Kesalahan Input:** Kombinasi Validitas **'{validitas}'** dan Kendali **'{kendali}'** tidak tersedia pada Tabel 14 resmi. Silakan ubah kombinasi Anda.")
    valid_to_calculate = False

# VALIDASI OTOMATIS 3: Cek Konsistensi Logika Target & Realisasi
if not iki_baru and target_lalu == 0 and realisasi_lalu == 0:
    st.info("ℹ️ Tips: Jika tidak memiliki data tahun lalu, centang opsi 'IKI Baru tanpa historis'.")

# --- PROSES PERHITUNGAN (HANYA BERJALAN JIKA VALID) ---
if valid_to_calculate:
    # 1. Hitung Bobot Kualitas IKI (Tabel 14)
    bobot_iki = 1.0
    if validitas == "Exact" and kendali == "Low": bobot_iki = 1.2
    elif validitas == "Exact" and kendali == "Moderate": bobot_iki = 1.15
    elif validitas == "Proxy" and kendali == "Low": bobot_iki = 1.1
    elif validitas == "Proxy" and kendali == "Moderate": bobot_iki = 1.0
    elif validitas == "Proxy" and kendali == "High": bobot_iki = 0.9
    elif validitas == "Activity" and kendali == "Moderate": bobot_iki = 0.8
    elif validitas == "Activity" and kendali == "High": bobot_iki = 0.6
    
    # 2. Hitung Capaian IKI (Sederhana untuk demo Maximize)
    capaian_iki = (realisasi_ini / target_ini) * 100 if target_ini > 0 else 100.0
    if polaritas == "Minimize" and target_ini > 0:
        capaian_iki = (target_ini / realisasi_ini) * 100 if realisasi_ini > 0 else 0.0

    # 3. Kalibrasi Batas Maksimal (KMK 127)
    nhk_kalibrasi = min(capaian_iki, 115.0)  # Batas non-PPTM
    npk_kalibrasi = min(npk_awal, 115.0)
    
    # 4. Rumus NKP Awal (75% NHK + 25% NPK)
    nkp_awal = (0.75 * nhk_kalibrasi) + (0.25 * npk_kalibrasi)
    nkp_koreksi = nkp_awal + nilai_koreksi - hukdis - dampak_disiplin
    
    # 5. Bobot Individu vs NKO
    bobot_individu = 0.9 if nkp_koreksi < nko_unit else 0.7 # Asumsi pelaksana
    nkp_final = min(max(nkp_koreksi, 0.0), 120.0)

    # TAMPILKAN METRIK UTAMA
    st.success("✅ Seluruh data valid! Berikut hasil estimasinya:")
    
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Bobot Kualitas IKI", value=f"{bobot_iki}")
    m2.metric(label="Capaian IKI", value=f"{capaian_iki:.2f}%")
    m3.metric(label="NKP FINAL (0-120)", value=f"{nkp_final:.2f}")
    
else:
    st.warning("⚠️ Perhitungan dihentikan sementara. Perbaiki kesalahan di atas untuk melihat skor NKP Anda.")
