import streamlit as st
import pandas as pd

st.set_page_config(page_title="Buscador OSECAC Miramar", layout="centered")
st.title("🔎 Buscador Interno OSECAC Miramar")

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def cargar_datos():
    try:
        url_osecac = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"
        url_faba = "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv"

        df1 = pd.read_csv(url_osecac)
        df1["tipo"] = "OSECAC"

        df2 = pd.read_csv(url_faba)
        df2["tipo"] = "FABA"

        df_total = pd.concat([df1, df2], ignore_index=True)

        return df_total

    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

df = cargar_datos()

# =========================
# BUSCADOR
# =========================
pregunta = st.text_input("¿Qué dato buscás?")

if pregunta and not df.empty:
    pregunta = pregunta.strip()

    resultados = df[
        df.astype(str)
        .apply(lambda row: row.str.contains(pregunta, case=False, na=False).any(), axis=1)
    ]

    if not resultados.empty:
        st.success(f"Se encontraron {len(resultados)} resultado(s):")
        st.dataframe(resultados, use_container_width=True)
    else:
        st.warning("No se encontraron coincidencias.")

# =========================
# MENSAJE SI NO HAY DATOS
# =========================
if df.empty:
    st.warning("No se pudieron cargar los datos.")
