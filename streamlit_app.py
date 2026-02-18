import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="GemStone AI",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. ESTILIZAÇÃO CSS (Design High-End) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@400;700&display=swap');

    .stApp {
        background-color: #051e16;
        color: #e0e0e0;
    }
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: #ffffff;
    }
    
    /* Uploader customizado */
    [data-testid='stFileUploader'] {
        width: 100%;
    }
    [data-testid='stFileUploader'] section {
        background-color: #0f2922;
        border: 2px dashed #10b981;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
    }
    [data-testid='stFileUploader'] section:hover {
        background-color: #163c32;
    }
    
    /* Botões */
    .stButton>button {
        background-color: #10b981;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #059669;
        border: 1px solid #ffffff;
    }
    
    /* Cards de Resultado */
    .metric-card {
        background-color: #0f2922;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #10b981;
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    img {
        border-radius: 10px;
    }
    
    /* Expander Webcam */
    .streamlit-expanderHeader {
        background-color: #0f2922;
        color: #10b981;
        border-radius: 5px;
    }
    
    .debug-box {
        font-size: 12px;
        color: #666;
        margin-top: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DICIONÁRIO DE DADOS ---
gem_info = {
    "Alexandrite": {"name": "Alexandrita", "mohs": "8.5", "origin": "Rússia, Brasil", "desc": "Muda de cor: verde à luz do dia e vermelha à luz incandescente."},
    "Almandine": {"name": "Almandina (Granada)", "mohs": "7.5 - 8.5", "origin": "Brasil, Índia", "desc": "Tipo comum de Granada. Cor vermelho-escuro profundo a violeta."},
    "Amazonite": {"name": "Amazonita", "mohs": "6.0 - 6.5", "origin": "Brasil, Rússia", "desc": "Variedade verde do feldspato, nomeada em homenagem ao Rio Amazonas."},
    "Amethyst": {"name": "Ametista", "mohs": "7.0", "origin": "Brasil, Uruguai", "desc": "Variedade violeta do quartzo, apreciada por sua cor vibrante."},
    "Aquamarine": {"name": "Água-Marinha", "mohs": "7.5 - 8.0", "origin": "Brasil, Nigéria", "desc": "Pedra preciosa azul-claro a azul-esverdeado."},
    "Beryl Golden": {"name": "Berilo Dourado", "mohs": "7.5 - 8.0", "origin": "Brasil, Namíbia", "desc": "Berilo de cor amarelo limão a amarelo dourado."},
    "Blue Lace Agate": {"name": "Ágata Blue Lace", "mohs": "6.5 - 7.0", "origin": "Namíbia", "desc": "Ágata com faixas azul-claras delicadas."},
    "Carnelian": {"name": "Cornalina", "mohs": "6.5 - 7.0", "origin": "Índia, Brasil", "desc": "Variedade de calcedônia vermelho-alaranjada."},
    "Citrine": {"name": "Citrino", "mohs": "7.0", "origin": "Brasil", "desc": "Quartzo amarelo a laranja, associado à prosperidade."},
    "Diamond": {"name": "Diamante", "mohs": "10.0", "origin": "África, Rússia", "desc": "Material natural mais duro da Terra, carbono puro."},
    "Emerald": {"name": "Esmeralda", "mohs": "7.5 - 8.0", "origin": "Colômbia, Brasil", "desc": "Berilo verde precioso, famoso por suas inclusões."},
    "Garnet Red": {"name": "Granada Vermelha", "mohs": "6.5 - 7.5", "origin": "Índia, EUA", "desc": "Mineral silicato vermelho profundo."},
    "Grossular": {"name": "Grossularia (Granada)", "mohs": "6.5 - 7.5", "origin": "Canadá, África", "desc": "Granada que pode variar do incolor ao verde, amarelo e marrom."},
    "Hessonite": {"name": "Hessonita (Granada)", "mohs": "6.5 - 7.5", "origin": "Sri Lanka", "desc": "Conhecida como 'Pedra de Canela' por sua cor laranja-amarronzada."},
    "Jade": {"name": "Jade", "mohs": "6.0 - 7.0", "origin": "Mianmar, China", "desc": "Pedra ornamental valorizada no Oriente, símbolo de pureza."},
    "Jasper": {"name": "Jaspe", "mohs": "6.5 - 7.0", "origin": "Global", "desc": "Variedade opaca de calcedônia, geralmente vermelha, amarela ou marrom."},
    "Kunzite": {"name": "Kunzita", "mohs": "6.5 - 7.0", "origin": "Afeganistão, Brasil", "desc": "Pedra rosa a lilás, variedade do mineral espodumena."},
    "Labradorite": {"name": "Labradorita", "mohs": "6.0 - 6.5", "origin": "Canadá, Madagáscar", "desc": "Feldspato famoso por sua iridescência espetacular (labradorescência)."},
    "Lapis Lazuli": {"name": "Lápis-Lazúli", "mohs": "5.0 - 5.5", "origin": "Afeganistão", "desc": "Rocha azul profundo usada desde a antiguidade."},
    "Malachite": {"name": "Malaquita", "mohs": "3.5 - 4.0", "origin": "Congo, Rússia", "desc": "Carbonato de cobre verde com padrões de faixas."},
    "Moonstone": {"name": "Pedra da Lua", "mohs": "6.0 - 6.5", "origin": "Sri Lanka, Índia", "desc": "Exibe um brilho azulado ou prateado misterioso."},
    "Onyx Black": {"name": "Ônix Preto", "mohs": "7.0", "origin": "Brasil, Índia", "desc": "Calcedônia preta, popular em joias masculinas."},
    "Opal": {"name": "Opala", "mohs": "5.5 - 6.5", "origin": "Austrália", "desc": "Famosa por seu jogo de cores iridescente."},
    "Peridot": {"name": "Peridoto", "mohs": "6.5 - 7.0", "origin": "EUA, Egito", "desc": "Gema que ocorre apenas em verde-oliva."},
    "Pyrope": {"name": "Piropo (Granada)", "mohs": "7.0 - 7.5", "origin": "África do Sul, EUA", "desc": "Granada de cor vermelho-sangue intenso."},
    "Quartz Rose": {"name": "Quartzo Rosa", "mohs": "7.0", "origin": "Brasil", "desc": "Pedra rosa suave, símbolo do amor incondicional."},
    "Quartz Smoky": {"name": "Quartzo Fumê", "mohs": "7.0", "origin": "Brasil, Suíça", "desc": "Quartzo marrom translúcido a cinza."},
    "Rhodolite": {"name": "Rodolita (Granada)", "mohs": "7.0 - 7.5", "origin": "Tanzânia, Brasil", "desc": "Granada rosa-framboesa a vermelho-púrpura."},
    "Ruby": {"name": "Rubi", "mohs": "9.0", "origin": "Mianmar, Moçambique", "desc": "Gema vermelha valiosa, corindo."},
    "Sapphire Blue": {"name": "Safira Azul", "mohs": "9.0", "origin": "Sri Lanka", "desc": "Símbolo de nobreza e sabedoria."},
    "Sapphire Pink": {"name": "Safira Rosa", "mohs": "9.0", "origin": "Madagascar", "desc": "Variação rara e romântica da safira."},
    "Sapphire Yellow": {"name": "Safira Amarela", "mohs": "9.0", "origin": "Tailândia, Austrália", "desc": "Safira brilhante e ensolarada."},
    "Tanzanite": {"name": "Tanzanita", "mohs": "6.5", "origin": "Tanzânia", "desc": "Gema azul-violeta encontrada apenas em um lugar na Terra."},
    "Tiger Eye": {"name": "Olho de Tigre", "mohs": "7.0", "origin": "África do Sul", "desc": "Pedra dourada com efeito de olho de gato."},
    "Topaz": {"name": "Topázio", "mohs": "8.0", "origin": "Brasil", "desc": "Disponível em várias cores, Imperial e Azul são famosos."},
    "Turquoise": {"name": "Turquesa", "mohs": "5.0 - 6.0", "origin": "Irã, EUA", "desc": "Mineral azul-esverdeado opaco."},
    "Tsavorite": {"name": "Tsavorita (Granada)", "mohs": "7.0 - 7.5", "origin": "Quênia, Tanzânia", "desc": "Granada verde vibrante, rivaliza com a esmeralda."},
    "Zircon": {"name": "Zircão", "mohs": "7.5", "origin": "Austrália", "desc": "Gema natural de alto brilho."}
}

# --- 4. FUNÇÕES DE BACKEND (Otimizadas para Cloud) ---
@st.cache_resource
def load_model():
    # Lista de locais possíveis onde o modelo pode estar
    possible_paths = [
        "models/gemstone_model.h5",   # Estrutura recomendada para GitHub
        "gemstone_model.h5",          # Se estiver na raiz
        "../models/gemstone_model.h5",# Estrutura local VS Code
        "models/gemstone_model.h5"         # Backup modelo simples
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                return tf.keras.models.load_model(path)
            except:
                continue # Tenta o próximo se der erro
                
    st.error("ERRO CRÍTICO: Modelo .h5 não encontrado! Verifique se a pasta 'models' foi enviada para o GitHub.")
    return None

def get_class_names():
    # Tenta ler do arquivo classes.txt (Ideal para Cloud)
    if os.path.exists("classes.txt"):
        with open("classes.txt", "r") as f:
            # Lê linhas e remove quebras de linha (\n)
            return [line.strip() for line in f.readlines() if line.strip()]
    
    # Fallback: Tenta ler da pasta local (Só funciona no VS Code)
    elif os.path.exists("../data/train"):
        return sorted(os.listdir("../data/train"))
    
    st.warning("Aviso: classes.txt não encontrado. O aplicativo pode errar os nomes.")
    return []

def process_image(image_data, model):
    if model is None:
        return None
        
    size = (224, 224)
    image = ImageOps.fit(image_data, size, Image.Resampling.LANCZOS)
    image = image.convert('RGB') # Garante 3 canais
    img = np.asarray(image)
    img = img / 255.0
    img_reshape = img[np.newaxis, ...]
    
    prediction = model.predict(img_reshape)
    return prediction

# --- 5. INTERFACE PRINCIPAL ---

st.markdown("<h1 style='text-align: center; font-size: 3rem;'>GemStone AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aecbb6; margin-bottom: 20px;'>Identificação profissional de gemas via Inteligência Artificial.</p>", unsafe_allow_html=True)

with st.spinner('Carregando inteligência artificial...'):
    model = load_model()
    class_names = get_class_names()

# --- INPUT UNIFICADO ---
st.markdown("### 💎 Analisar Pedra")

# Botão principal (Funciona como Drag&Drop no PC e Câmera no Celular)
upload_file = st.file_uploader(
    "Tirar Foto ou Escolher da Galeria", 
    type=["jpg", "png", "jpeg"],
    key="main_uploader"
)

# Opção Webcam PC (Escondida)
camera_file = None
with st.expander("📷 Webcam (Apenas PC)"):
    camera_file = st.camera_input("Capturar agora")

# Lógica de prioridade
image_to_process = camera_file if camera_file is not None else upload_file

if image_to_process is not None:
    image = Image.open(image_to_process)
    
    col_img, col_data = st.columns([1, 1.5])
    
    with col_img:
        st.image(image, use_container_width=True, caption="Amostra")
    
    with col_data:
        if st.button("🔍 Identificar Gema", type="primary"):
            if model is None:
                st.error("Modelo não carregado.")
            else:
                with st.spinner('Processando estrutura...'):
                    predictions = process_image(image, model)
                    
                    if predictions is not None:
                        result_index = np.argmax(predictions)
                        confidence = np.max(predictions) * 100
                        
                        # Proteção contra lista de classes desatualizada
                        if result_index < len(class_names):
                            pedra_ingles = class_names[result_index]
                        else:
                            pedra_ingles = "Desconhecido"

                        # Busca info
                        info = gem_info.get(pedra_ingles, {
                            "name": pedra_ingles, 
                            "mohs": "?", 
                            "origin": "?", 
                            "desc": "Dados técnicos ainda não catalogados."
                        })

                        st.markdown(f"""
                            <div class="metric-card">
                                <h2 style="color: #10b981; margin:0; text-transform: uppercase;">{info['name']}</h2>
                                <p style="font-size: 14px; color: #ccc;">Confiança IA: <b>{confidence:.1f}%</b></p>
                                <hr style="border-color: #10b981; opacity: 0.3;">
                                <p style="margin-top: 10px;"><b>📜 Sobre:</b> {info['desc']}</p>
                                <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                                    <div>
                                        <span style="font-size: 11px; color: #10b981;">DUREZA (MOHS)</span><br>
                                        <span style="font-size: 16px; font-weight: bold;">{info['mohs']}</span>
                                    </div>
                                    <div>
                                        <span style="font-size: 11px; color: #10b981;">ORIGEM</span><br>
                                        <span style="font-size: 16px; font-weight: bold;">{info['origin']}</span>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Debug discreto no rodapé
                        st.markdown(f"<div class='debug-box'>ID Técnico: {pedra_ingles}</div>", unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="text-align: center; padding: 40px; border: 1px dashed #333; border-radius: 10px; opacity: 0.5;">
            <p>Aguardando amostra...</p>
        </div>
    """, unsafe_allow_html=True)