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
# ESTILOS (MISMA LÍNEA)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background-color: #fffde7; color: #333; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #fff9c4 !important;
    border-right: 1px solid #f9a825;
}

/* Headers */
h1 { color: #f57f17 !important; }
h2, h3 { color: #e65100 !important; }

/* Inputs */
textarea, input[type="text"] {
    background-color: #fffff0 !important;
    border: 1px solid #f9a825 !important;
    border-radius: 6px !important;
}

/* Botones */
.stButton > button {
    background: #f9a825 !important;
    color: white !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover {
    background: #f57f17 !important;
}

/* Cards */
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
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 Image Analyzer")
    st.markdown("Analiza imágenes con IA")
    st.markdown("---")

    st.markdown("### Configuración")
    ke = st.text_input("API Key OpenAI", type="password")

    if ke:
        os.environ['OPENAI_API_KEY'] = ke

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
# FUNCIÓN
# ─────────────────────────────────────────────
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# ─────────────────────────────────────────────
# CARGA DE IMAGEN
# ─────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)

st.markdown("### 🖼️ Cargar imagen")
uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# OPCIONES
# ─────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)

st.markdown("### ⚙️ Opciones de análisis")

show_details = st.toggle("Agregar contexto adicional", value=False)

additional_details = ""
if show_details:
    additional_details = st.text_area(
        "Describe qué quieres saber específicamente:",
        placeholder="Ej: enfócate en los objetos, emociones, contexto histórico..."
    )

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# BOTÓN
# ─────────────────────────────────────────────
analyze_button = st.button("🔍 Analizar imagen")

# ─────────────────────────────────────────────
# PROCESAMIENTO
# ─────────────────────────────────────────────
if uploaded_file is not None and ke and analyze_button:

    client = OpenAI(api_key=ke)

    with st.spinner("Analizando imagen..."):
        base64_image = encode_image(uploaded_file)

        prompt_text = "Describe detalladamente lo que ves en la imagen en español."

        if additional_details:
            prompt_text += f"\n\nContexto adicional:\n{additional_details}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ],
            }
        ]

        try:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("### 🧠 Resultado del análisis")

            full_response = ""
            placeholder = st.empty()

            for chunk in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
                stream=True
            ):
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {e}")

# ─────────────────────────────────────────────
# VALIDACIONES
# ─────────────────────────────────────────────
elif analyze_button and not uploaded_file:
    st.warning("⚠️ Sube una imagen primero")

elif analyze_button and not ke:
    st.warning("⚠️ Ingresa tu API Key")
