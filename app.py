import os
import streamlit as st
import base64
from openai import OpenAI

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Análisis de Imagen",
    page_icon="🤖",
    layout="wide",
)

# ─────────────────────────────────────────────
# ESTILOS (MISMO TEMA)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #fffde7; }

[data-testid="stSidebar"] {
    background-color: #fff9c4 !important;
    border-right: 1px solid #f9a825;
}

h1 { color: #f57f17 !important; }

.stButton > button {
    background: #f9a825 !important;
    color: white !important;
    border-radius: 6px !important;
    width: 100%;
}

.header-card {
    background: #fff8e1;
    border-left: 5px solid #f9a825;
    padding: 28px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.section-card {
    background: #fff8e1;
    border: 1px solid #ffe082;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-card">
    <h1>🤖 Análisis de Imagen</h1>
    <p>Interpreta imágenes y obtén descripciones inteligentes en segundos</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# API KEY
# ─────────────────────────────────────────────
ke = st.text_input("🔑 API Key OpenAI", type="password")

if ke:
    os.environ['OPENAI_API_KEY'] = ke
    client = OpenAI(api_key=ke)
else:
    st.warning("Por favor ingresa tu API Key")

# ─────────────────────────────────────────────
# FUNCIÓN
# ─────────────────────────────────────────────
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# ─────────────────────────────────────────────
# CONTENEDOR 1 → CARGA (ANTES VACÍO)
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-card">
    <h2>🖼️ Cargar imagen</h2>
    <p>Sube una imagen para analizar</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["jpg","png","jpeg"])

if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONTENEDOR 2 → OPCIONES (ANTES VACÍO)
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-card">
    <h2>⚙️ Opciones de análisis</h2>
    <p>Sube una imagen para analizar</p>
</div>
""", unsafe_allow_html=True)

show_details = st.toggle("Agregar contexto adicional")

additional_details = ""
if show_details:
    additional_details = st.text_area(
        "Describe qué quieres analizar:",
        placeholder="Ej: analiza emociones, estilo, objetos específicos..."
    )

analyze_button = st.button("🚀 Analizar imagen")

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RESULTADO
# ─────────────────────────────────────────────
if uploaded_file and ke and analyze_button:

    with st.spinner("Analizando imagen..."):
        base64_image = encode_image(uploaded_file)

        prompt = "Describe la imagen en español de forma clara y estructurada."

        if additional_details:
            prompt += f"\n\nContexto adicional:\n{additional_details}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ],
            }
        ]

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🤖 Resultado del análisis")

        full_response = ""
        placeholder = st.empty()

        for chunk in client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True,
            max_tokens=1200
        ):
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# VALIDACIONES
# ─────────────────────────────────────────────
elif analyze_button:
    if not uploaded_file:
        st.warning("⚠️ Sube una imagen primero")
    if not ke:
        st.warning("⚠️ Ingresa tu API Key")
