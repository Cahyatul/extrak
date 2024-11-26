import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt

# Judul aplikasi
st.title("Ekstraktor SQLite DB3 ke Excel dan Grafik")
st.write("Unggah file SQLite (.db3) untuk mengekstrak data tabel ke Excel dan membuat grafik.")

# Unggah beberapa file SQLite
uploaded_files = st.file_uploader("Unggah file SQLite (.db3)", type="db3", accept_multiple_files=True)

if uploaded_files:
    table_selection = {}
    all_dataframes = {}

    for file in uploaded_files:
        st.subheader(f"File: {file.name}")
        try:
            # Membuka koneksi SQLite
            conn = sqlite3.connect(file.name)
            # Mendapatkan daftar tabel
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

            # Membaca data dari tabel yang dipilih
            conn = sqlite3.connect(file.name)
            for table in selected_tables:
                try:
                    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                    all_dataframes[f"{file.name}_{table}"] = df
                except Exception as e:
                    st.error(f"Gagal membaca tabel {table} dari {file.name}. Error: {e}")
            conn.close()
        except Exception as e:
            st.error(f"Gagal membaca database dari {file.name}. Error: {e}")

    # Tombol untuk mengunduh data sebagai Excel
    if st.button("Ekstrak Data ke Excel"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for key, df in all_dataframes.items():
                sheet_name = key[:31]  # Maks 31 karakter untuk nama sheet Excel
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)

        st.download_button(
            label="Unduh file Excel",
            data=output,
            file_name="ekstrak_db3.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Menampilkan grafik berdasarkan tabel yang dipilih
    st.subheader("Grafik dari Data")
    selected_table_for_plot = st.selectbox(
        "Pilih tabel untuk menampilkan grafik:",
        options=list(all_dataframes.keys())
    )

    if selected_table_for_plot:
        df_to_plot = all_dataframes[selected_table_for_plot]
        st.write("Data Tabel:")
        st.write(df_to_plot)

        numeric_columns = df_to_plot.select_dtypes(include="number").columns.tolist()
        if numeric_columns:
            x_axis = st.selectbox("Pilih kolom X:", options=numeric_columns)
            y_axis = st.selectbox("Pilih kolom Y:", options=numeric_columns)

            if x_axis and y_axis:
                fig, ax = plt.subplots()
                ax.plot(df_to_plot[x_axis], df_to_plot[y_axis], marker="o")
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                ax.set_title(f"Grafik {y_axis} terhadap {x_axis}")
                st.pyplot(fig)
        else:
            st.warning("Tabel tidak memiliki kolom numerik untuk membuat grafik.")
