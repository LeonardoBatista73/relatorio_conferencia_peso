import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title='Relatório de conferência por peso', layout='centered')

# 1. INICIALIZAÇÃO
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=[
        'AL', 'Descrição', 'Volumes Tara', 'Peso Médio', 'Volumes Palete', 'Peso Bruto', 'Peso Líquido', 'Diferença'
    ])

# Função para resetar os campos após salvar
def limpar_campos():
    st.session_state.al_input = ""
    st.session_state.tara_input = 1
    st.session_state.peso_total_input = 0.0
    st.session_state.qtd_vol_input = 0
    st.session_state.peso_bruto_input = 0.0

# Título
st.markdown('<h1 style="text-align: center; font-size: 30px;">Relatório de conferência por peso</h1>', unsafe_allow_html=True)

st.write('')
st.write('')

# 2. CARREGAR DADOS
try:
    produtos_local20 = pd.read_excel('Produtos Local 20.xlsx', engine='openpyxl')
    produtos_local20['Código'] = produtos_local20['Código'].astype(str).str.strip()
except:
    st.error("Arquivo 'Produtos Local 20.xlsx' não encontrado!")
    st.stop()

# 3. INTERAÇÃO DO USUÁRIO
col1, col2 = st.columns([1, 2])

with col1:
    # Usamos a KEY para podermos limpar depois
    al_busca = st.text_input('Digite o AL:', key='al_input')

# Busca descrição
al_resultado = produtos_local20[produtos_local20['Código'].str.upper() == al_busca.upper()]
descricao_al_resultado = al_resultado['Descrição'].values[0] if not al_resultado.empty else "AL não encontrado"

with col2:
    st.write('**Descrição AL:**')
    st.write(descricao_al_resultado)

col4, col5 = st.columns(2)
with col4:
    und_tara = st.number_input('Volumes para Tara:', min_value=1, step=1, format='%d', key='tara_input')
with col5:
    peso_total_und = st.number_input('Peso total aferido:', min_value=0.0, format="%.3f", key='peso_total_input')

# Cálculos intermediários
peso_medio_kg_und = round(peso_total_und / und_tara, 3) if und_tara > 0 else 0

st.markdown(f"""<div style="background-color: #172d43; padding: 10px; border-radius: 5px; margin: 10px 0;">
    <h3 style="text-align: center; color: white; margin:0;">Peso médio: {peso_medio_kg_und} kg</h3></div>""", unsafe_allow_html=True)

col7, col8 = st.columns(2)
with col7:
    qtd_volume_palete = st.number_input('Qtd volumes no palete:', min_value=0, step=1, format='%d', key='qtd_vol_input')
    peso_liquido_plt = round(qtd_volume_palete * peso_medio_kg_und, 3)
    st.markdown(f"""<div style="background-color: #173928; padding: 10px; border-radius: 5px; color: white; text-align: center;">
        <b>Peso líquido:</b> {peso_liquido_plt} kg</div>""", unsafe_allow_html=True)

with col8:
    peso_bruto_plt = st.number_input('Peso Bruto do Palete:', min_value=0.0, format="%.3f", key='peso_bruto_input')
    st.markdown(f"""<div style="background-color: #444; padding: 10px; border-radius: 5px; color: white; text-align: center;">
        <b>Peso Bruto:</b> {peso_bruto_plt} kg</div>""", unsafe_allow_html=True)

dif_peso_palete = round(peso_bruto_plt - peso_liquido_plt, 3)

st.write('')

# Exibindo a diferença do Bruto e Liquido
st.markdown(f"""<div style="background-color: #3e4116; padding: 10px; border-radius: 5px; color: white; text-align: center;">
        <b>Diferença Final:</b> {dif_peso_palete} kg</div>""", unsafe_allow_html=True)

st.write('')

# 4. BOTÃO SALVAR
if st.button('✅ Confirmar e salvar no relatório', use_container_width=True):
    if al_busca != "" and descricao_al_resultado != "AL não encontrado":
        # Primeiro: Capturamos os dados
        novo_registro = {
            'AL': al_busca,
            'Descrição': descricao_al_resultado,
            'Volumes Tara': und_tara,
            'Peso Médio': peso_medio_kg_und,
            'Volumes Palete': qtd_volume_palete,
            'Peso Bruto': peso_bruto_plt,
            'Peso Líquido': peso_liquido_plt,
            'Diferença': dif_peso_palete
        }
        
        # Segundo: Salvamos no histórico
        st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo_registro])], ignore_index=True)
        
        # Terceiro: Limpamos os campos usando um método que não gera conflito
        # Em vez de chamar limpar_campos(), vamos apenas resetar e dar rerun
        for key in ['al_input', 'peso_total_input', 'peso_bruto_input', 'qtd_vol_input']:
            if key in st.session_state:
                del st.session_state[key] # Deletar a chave força o widget a voltar ao valor inicial
        
        st.success("Dados registrados!")
        st.rerun() 
    else:
        st.error("Por favor, insira um AL válido antes de salvar.")

# 5. EXIBIÇÃO DA TABELA ACUMULADA
st.write("---")
st.subheader("📋 Conferências Realizadas")
st.dataframe(st.session_state.historico, use_container_width=True)

col9, col10 = st.columns(2)

# Botão para limpar o histórico todo (opcional)
with col9:
    if st.button("🧹 Limpar tabela"):
        st.session_state.historico = pd.DataFrame(columns=st.session_state.historico.columns)
        st.rerun()

with col10:
    if not st.session_state.historico.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            st.session_state.historico.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Baixar relatório em Excel",
            data=buffer,
            file_name='conferencia.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
