import streamlit as st
import joblib
import pandas as pd
from geopy.geocoders.opencage import OpenCage
from geopy.distance import geodesic
import os
import time
from dotenv import load_dotenv

# --- Configuração da página ---
st.set_page_config(page_title="Previsor de Imóveis - BH", layout="wide")
load_dotenv()
MINHA_API_KEY = os.getenv("OPENCAGE_API_KEY")

# --- Pontos de Interesse em BH ---
PONTOS_INTERESSE = {
    'praca_da_liberdade': (-19.932, -43.935),
    'lagoa_da_pampulha': (-19.829, -43.954),
    'parque_americo_renne': (-19.923, -43.947),
    'parque_das_mangabeiras': (-19.955, -43.958),
    'circuito_da_liberdade': (-19.933, -43.937),
    'mercado_central': (-19.924, -43.935),
    'igreja_sao_jose': (-19.924, -43.937)
}

MAE_MODELO = 191111.21

# --- Funções ---
@st.cache_resource
def carregar_recursos():
    modelo = joblib.load('joblib/modelo_xgb.joblib') if os.path.exists('joblib/modelo_xgb.joblib') else None
    colunas = joblib.load('joblib/model_columns.joblib') if os.path.exists('joblib/model_columns.joblib') else None
    return modelo, colunas

@st.cache_data
def buscar_dados_geograficos(endereco_query, api_key):
    try:
        geolocator = OpenCage(api_key=api_key, user_agent="app_previsao_imoveis_bh")
        location = geolocator.geocode(endereco_query, timeout=30)
        time.sleep(1)
        if location and location.raw:
            lat, lon = location.latitude, location.longitude
            components = location.raw.get('components', {})
            bairro = components.get('suburb', components.get('city_district', 'Desconhecido'))
            return location, lat, lon, bairro
        else:
            return None, None, None, None
    except Exception as e:
        return f"ERRO_API: {e}", None, None, None

# --- Carrega modelo e colunas ---
modelo, colunas_modelo = carregar_recursos()

# --- Título ---
st.title('Previsor de Valor de Imóveis em Belo Horizonte')

# --- Sidebar ---
st.sidebar.header('Insira as Características do Imóvel')
endereco = st.sidebar.text_input('Endereço ou CEP do Imóvel:', placeholder='Ex: Av. Afonso Pena, 1234')
tamanho = st.sidebar.number_input('Área (m²)', min_value=20, max_value=1000, value=80, step=5)
quartos = st.sidebar.slider('Quantidade de Quartos', min_value=1, max_value=6, value=3)
banheiros = st.sidebar.slider('Quantidade de Banheiros', min_value=1, max_value=6, value=2)
vagas = st.sidebar.slider('Vagas de Garagem', min_value=0, max_value=5, value=1)
st.sidebar.divider()
calcular = st.sidebar.button('Estimar Valor', type="primary", use_container_width=True)

if calcular:
    if not endereco:
        st.warning("Por favor, insira um endereço para iniciar a estimativa.")
    elif modelo is None or colunas_modelo is None:
        st.error("ERRO: Arquivos do modelo ou de colunas não encontrados.")
    else:
        with st.spinner("Buscando e validando o endereço..."):
            query = f"{endereco}, Belo Horizonte, MG, Brazil"
            location, lat, lon, bairro = buscar_dados_geograficos(query, MINHA_API_KEY)

            if isinstance(location, str) and location.startswith("ERRO_API"):
                st.error(f"Ocorreu um erro ao contatar a API: {location}")
            elif location is None:
                st.error("Endereço não encontrado. Use um endereço mais específico ou um CEP.")
            else:
                st.header(f"Análise para: {location.address}")
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.subheader("Localização no Mapa")
                    st.map(pd.DataFrame({'latitude': [lat], 'longitude': [lon]}), zoom=15)

                with col2:
                    st.subheader("Estimativa Financeira")

                    # --- Distâncias ---
                    distancias = {f'dist_{nome}_km': geodesic((lat, lon), coord).kilometers
                                  for nome, coord in PONTOS_INTERESSE.items()}

                    # --- Cria DataFrame base ---
                    df_base = pd.DataFrame([{
                        'tamanho (m²)': tamanho,
                        'qtd_quartos': quartos,
                        'qtd_banheiros': banheiros,
                        'qtd_vagas_garagem': vagas,
                        'especial': 0,
                        'bairro_norm': 0,
                        **distancias
                    }])

                    # --- Dummy de bairro ---
                    if 'bairro_norm' in colunas_modelo:
                        df_base['bairro_norm'] = 0

                    # --- Ajusta colunas para coincidir com o modelo ---
                    colunas_input = [c for c in colunas_modelo if c != 'preco']
                    for col in colunas_input:
                        if col not in df_base.columns:
                            df_base[col] = 0
                    df_final = df_base[colunas_input].astype(float)

                    # --- Previsão ---
                    previsao = modelo.predict(df_final)[0]
                    valor_min = previsao - MAE_MODELO
                    valor_max = previsao + MAE_MODELO

                    st.metric("Valor de Venda Estimado", f"R$ {previsao:,.2f}")
                    st.divider()

                    # --- Substituindo st.metric por HTML para Faixa Mínima e Máxima ---
                    sub_col1, sub_col2 = st.columns(2)

                    sub_col1.markdown(f"""
                    <div style='font-size:14px;'>Faixa Mínima</div>
                    <div style='font-size:20px; font-weight:bold;'>R$ {valor_min:,.2f}</div>
                    """, unsafe_allow_html=True)

                    sub_col2.markdown(f"""
                    <div style='font-size:14px;'>Faixa Máxima</div>
                    <div style='font-size:20px; font-weight:bold;'>R$ {valor_max:,.2f}</div>
                    """, unsafe_allow_html=True)