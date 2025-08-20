import streamlit as st
import asyncio
import httpx

# --- Data untuk Konselor Adiksi ---
addiction_diagnoses_list = [
    "Nicotine Abuse/Depedence",
    "Substance-Induced Disorder",
    "Substance Intoxication/Withdrawal",
    "Substance Use Disorder",
    "Chronic Pain",
    "Medical Issue",
    "Adult Child Of An Alcoholic (ACA) Traits",
    "Anger",
    "Antisocial Behavior",
    "Anxiety",
    "ADHD Adolescent",
    "ADHD Adult",
    "Bipolar Disorder",
    "Borderline Traits",
    "Childhood Trauma",
    "Conduct Disorder/Delinquency",
    "Dangerousness/Lethality",
    "Dependent Traits",
    "Eating Disorder and Obesity",
    "Family Conflicts",
    "Gambling",
    "Grief/Loss Unresolved",
    "Impulsivity",
    "Legal Problems",
    "Narcissistic Traits",
    "OCD",
    "Oppositional Defiant Behavior",
    "Posttraumatic Stress Disorder (PTSD)",
    "Psychosis",
    "Self Care Deficits Primary",
    "Self Care Deficits Secondary",
    "Self Harm",
    "Sexual Abuse",
    "Sexual Promiscuity",
    "Sleep Disturbance",
    "Social Anxiety",
    "Spiritual Confusion",
    "Suicidal Ideation",
    "Unipolar Depression",
    "Treatment Resistance",
    "Relapse Proneness",
    "Living Environment Deficiency",
    "Occupational Problems",
    "Parent Child Relational Problem",
    "Partner Relational Conflicts",
    "Peer Group Negativity"
]

addiction_prompt_template = """
Sebagai konselor adiksi di sebuah lembaga rehabilitasi, buatlah catatan konseling dengan format SOAP (Subjective, Objective, Assessment, Planning) untuk klien yang menghadapi isu konseling berikut: {diagnosis}.

Gunakan deskripsi klien berikut untuk membuat catatan yang lebih spesifik:
{description}

Berikan informasi yang relevan untuk setiap bagian (S, O, A, P). Pastikan format keluarannya jelas, dengan setiap bagian diawali dengan S:, O:, A:, dan P:.

S: Tulis keluhan subjektif atau pernyataan klien.
O: Tulis data objektif seperti observasi perilaku, interaksi, dan ekspresi emosi klien selama sesi.
A: Tulis asesmen atau diagnosis fungsional berdasarkan data S dan O.
P: Buatlah rencana intervensi konseling yang relevan dan langkah selanjutnya. Rencana ini harus mencakup beberapa poin, di mana setiap poin intervensi diikuti oleh penjelasan satu kalimat yang menunjukkan bagaimana poin tersebut memenuhi kriteria SMART (Specific, Measurable, Achievable, Relevant, Time-bound).

Format keluaran harus seperti contoh berikut:
S: [Teks subjektif klien]
O: [Teks objektif konselor]
A: [Teks asesmen konselor]
P: 
1. [Poin Intervensi 1]. (SMART: [Satu kalimat penjelasan SMART])
2. [Poin Intervensi 2]. (SMART: [Satu kalimat penjelasan SMART])
...
"""

# Fungsi untuk membuat panggilan API async ke model Gemini
async def generate_text_from_model(prompt):
    api_key = st.session_state.get('api_key', None)
    if not api_key:
        st.error("Kesalahan: Kunci API tidak ditemukan. Silakan masukkan kunci API Anda.")
        return None

    try:
        chat_history = [{"role": "user", "parts": [{"text": prompt}]}]
        
        payload = {
            "contents": chat_history,
            "generationConfig": {"responseMimeType": "text/plain"}
        }
        
        apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
        
        async with httpx.AsyncClient() as client:
            for i in range(5):
                try:
                    response = await client.post(
                        apiUrl,
                        headers={"Content-Type": "application/json"},
                        json=payload,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
                        return result["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        st.error("Kesalahan: Format respons API tidak terduga.")
                        return None
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in [429, 503] and i < 4:
                        st.warning(f"Batas laju API terlampaui atau layanan tidak tersedia. Mencoba lagi dalam {2**i} detik...")
                        await asyncio.sleep(2**i)
                    else:
                        raise e
    except Exception as e:
        st.error(f"Kesalahan selama panggilan API: {e}")
        return None

async def generate_soap_note_async(diagnosis_key, description, prompt_template):
    prompt = prompt_template.format(diagnosis=diagnosis_key, description=description)
    with st.spinner("Sedang menghasilkan catatan SOAP..."):
        full_note_raw = await generate_text_from_model(prompt)
    if not full_note_raw:
        return "Gagal menghasilkan catatan SOAP. Pastikan kunci API Anda valid dan terisi."
    return full_note_raw

# Pengaturan halaman Streamlit
st.set_page_config(
    page_title="Generator Catatan SOAP Konselor Adiksi",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Judul dan penjelasan utama
st.title("Generator Catatan SOAP Konselor Adiksi")
st.write("Aplikasi ini menggunakan AI untuk membantu konselor adiksi membuat catatan SOAP yang profesional dan terstruktur.")

st.markdown("---")

st.markdown("## Cara Menggunakan Aplikasi")
st.markdown("### 🔑 Kunci API Google")
st.markdown("""
Aplikasi ini memanfaatkan model AI Google Gemini. Untuk menggunakannya, Anda harus memasukkan **kunci API** pribadi Anda.

1.  Kunjungi **Google AI Studio** di [https://aistudio.google.com/](https://aistudio.google.com/).
2.  Masuk dengan akun Google Anda dan ikuti petunjuk untuk membuat kunci API.
3.  Salin kunci API yang dibuat dan tempelkan di kolom yang tersedia di **sidebar** (panel samping).
""")

st.markdown("### ⚠️ Konsekuensi Biaya")
st.markdown("""
Penggunaan API Gemini memiliki batas gratis yang sangat besar. Namun, penting untuk dipahami bahwa setelah batas tersebut terlampaui, akan ada biaya yang dikenakan oleh Google. Aplikasi ini **TIDAK** mengenakan biaya apapun; biaya sepenuhnya dikelola oleh Google berdasarkan penggunaan kunci API Anda.

* **Model**: `gemini-2.5-flash`
* **Tarif**: Sekitar $0.0001 per 1.000 karakter (harga dapat berubah, cek situs Google AI untuk informasi terbaru).
* **Penting**: Kunci API Anda terhubung dengan akun Google Cloud Anda. Pantau penggunaan Anda di Google Cloud Console untuk menghindari biaya tak terduga.
""")

st.markdown("### 📝 Input Klien")
st.markdown("""
* **Pilih Isu Konseling**: Pilih dari daftar isu adiksi yang relevan dengan kasus klien.
* **Deskripsi Klien**: Masukkan detail spesifik tentang klien (usia, latar belakang, riwayat penggunaan, perilaku selama sesi, dll.). Semakin detail deskripsi Anda, semakin akurat catatan SOAP yang dihasilkan.
""")

st.markdown("### ✨ Konsep SMART pada Rencana (P)")
st.markdown("""
Bagian **P (Planning)** pada catatan SOAP akan dihasilkan dengan mengikuti konsep **SMART**. Setiap poin intervensi akan dilengkapi dengan penjelasan singkat yang menunjukkan bagaimana poin tersebut memenuhi kriteria SMART.
""")

st.markdown("---")

st.markdown("## Masukkan Informasi Anda")

# --- Masukan Kunci API di sidebar
with st.sidebar:
    st.subheader("🔑 Masukkan Kunci API Anda")
    api_key_input = st.text_input(
        "Kunci API Google",
        type="password",
        help="Anda dapat memperoleh kunci API dari Google AI Studio."
    )
    if api_key_input:
        st.session_state['api_key'] = api_key_input
        st.success("Kunci API berhasil disimpan!")
    
    if st.button("Hapus Kunci API"):
        if 'api_key' in st.session_state:
            del st.session_state['api_key']
            st.info("Kunci API telah dihapus dari sesi.")

# Tampilkan pesan jika kunci API belum dimasukkan
if 'api_key' not in st.session_state:
    st.warning("☝️ Silakan masukkan kunci API Anda di sidebar untuk menggunakan aplikasi.")
    st.stop()

# --- Bagian utama aplikasi
selected_issue = st.selectbox(
    "Pilih Isu Konseling Adiksi:",
    options=addiction_diagnoses_list,
    help="Pilih isu yang paling sesuai dengan kondisi klien."
)

patient_description = st.text_area(
    "Deskripsi Klien",
    height=150,
    help="Masukkan detail tentang klien, seperti usia, latar belakang, dan riwayat penggunaan zat atau perilaku.",
    placeholder="Contoh: Klien laki-laki, 32 tahun, datang karena diperintahkan oleh pengadilan. Klien menunjukkan sikap defensif dan kesulitan dalam menjalin kontak mata. Riwayat penggunaan alkohol dan kokain."
)

if st.button("Hasilkan Catatan SOAP Lengkap"):
    st.markdown("---")
    
    full_note = asyncio.run(generate_soap_note_async(selected_issue, patient_description, addiction_prompt_template))
    
    st.subheader("Catatan SOAP Lengkap")
    st.text_area(
        "Salin teks di bawah:",
        value=full_note,
        height=350,
        help="Klik di dalam kotak teks, lalu gunakan Ctrl+C (atau Cmd+C) untuk menyalin."
    )
    
    st.markdown("---")

st.info("Aplikasi ini dibuat sebagai contoh. Isi catatan harus disesuaikan dengan kondisi spesifik klien dan diverifikasi oleh tenaga profesional.")