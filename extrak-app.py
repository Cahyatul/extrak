import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO
!pip install streamlit pandas openpyxl matplotlib


# Judul aplikasi
st.title("Ekstraktor SQLite DB3 ke Excel")
st.write("Unggah file SQLite (.db3) dan ekstrak data tabel ke dalam format Excel.")

# Unggah beberapa file SQLite
uploaded_files = st.file_uploader("Unggah file SQLite (.db3)", type="db3", accept_multiple_files=True)

if uploaded_files:
    # Dictionary untuk menyimpan tabel yang dipilih dari setiap file
    table_selection = {}

    # Loop setiap file yang diunggah
    for file in uploaded_files:
        st.subheader(f"File: {file.name}")
        try:
            # Membuka koneksi SQLite
            conn = sqlite3.connect(file.name)
            # Mendapatkan daftar tabel di database
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
            table_list = tables["name"].tolist()
            conn.close()

            # Memilih tabel yang akan diekstrak
            selected_tables = st.multiselect(
                f"Pilih tabel dari {file.name}:",
                options=table_list,
                default=table_list
            )
            table_selection[file.name] = selected_tables
        except Exception as e:
            st.error(f"Gagal membaca tabel dari {file.name}. Error: {e}")

    # Tombol untuk memulai proses ekstraksi
    if st.button("Ekstrak ke Excel"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for file in uploaded_files:
                if file.name in table_selection:
                    conn = sqlite3.connect(file.name)
                    for table in table_selection[file.name]:
                        try:
                            # Membaca data tabel dan menulis ke Excel
                            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                            sheet_name = f"{file.name}_{table}"[:31]  # Maks 31 karakter untuk nama sheet
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                        except Exception as e:
                            st.error(f"Gagal mengekstrak tabel {table} dari {file.name}. Error: {e}")
                    conn.close()
        output.seek(0)

        # Tombol untuk mengunduh file Excel
        st.download_button(
            label="Unduh file Excel",
            data=output,
            file_name="ekstrak_db3.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
