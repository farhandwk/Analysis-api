from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import io

# Inisialisasi aplikasi Flask
app = Flask(__name__)
# Definisikan domain frontend mana saja yang diizinkan
origins = [
    "http://localhost:5173",  # Untuk development di lokal Anda
    "http://URL_FRONTEND_LIVE_ANDA" # Ganti dengan URL frontend live Anda nanti
]

CORS(app, origins=origins)


@app.route("/api/upload", methods=['POST'])
def upload_file():
    # Cek apakah ada file dalam request
    if 'file' not in request.files:
        return jsonify({"error": "Tidak ada file yang dikirim"}), 400
    
    file = request.files['file']
    
    # Cek jika pengguna tidak memilih file
    if file.filename == '':
        return jsonify({"error": "Tidak ada file yang dipilih"}), 400
    
    if file:
        try:
            # Kolom-kolim skala linkert
            kolom_likert = [
                'Seberapa puas kamu terhadap informasi teknis yang diberikan saat promosi acara berlangsung?   (seperti HTM, jadwal, pembicara yang terdapat di poster acara)',
                'Seberapa puas kamu terhadap informasi mengenai tujuan dan manfaat event yang disampaikan saat promosi acara berlangsung?',
                'Seberapa puas kamu terhadap edukasi yang diberikan oleh pembicara?',
                'Seberapa puas kamu terhadap ruang diskusi yang diberikan saat acara berlangsung?',
                'Seberapa puas kamu dengan keseluruhan acara ini?'
            ]

            nilai_likert = {
                'sangat tidak memuaskan': 1,
                'tidak memuaskan': 2,
                'netral': 3,
                'memuaskan': 4,
                'sangat memuaskan': 5
            }

            nama_kolom_baru = ['Q1_InfoTeknis', 'Q2_InfoTujuan', 'Q3_Edukasi', 'Q4_Diskusi', 'Q5_Keseluruhan']

            # Simpan nama file
            nama_file_asli = file.filename
            
            file.seek(0)
            
            # Berikan string tersebut ke Pandas untuk dibaca sebagai CSV
            df = pd.read_csv(file)
            # --------------------------------

            df_analisis = df[kolom_likert].copy()

            df_analisis.columns = nama_kolom_baru

            for kolom in nama_kolom_baru: # Gunakan nama baru untuk iterasi
                df_analisis[kolom] = df_analisis[kolom].astype(str).str.lower().str.strip()
            df_analisis.replace(nilai_likert, inplace=True)

            # Lakukan analisis deskriptif
            jumlah_baris, jumlah_kolom = df.shape
            statistik = df_analisis.describe().to_dict()

            matriks_korelasi = df_analisis.corr(method='spearman').to_dict()
            
            # Membangun respon JSON
            hasil_analisis = {
                "nama_file": nama_file_asli,
                "jumlah_baris": jumlah_baris,
                "jumlah_kolom": jumlah_kolom,
                "statistik": statistik,
                "korelasi" : matriks_korelasi
            }
            
            return jsonify(hasil_analisis)

        except Exception as e:
            # Mengembalikan error jika terjadi masalah saat pemrosesan
            return jsonify({"error": f"Gagal memproses file: {e}"}), 500

# Jalankan server saat skrip dieksekusi
if __name__ == "__main__":
    app.run(debug=True, port=5000)