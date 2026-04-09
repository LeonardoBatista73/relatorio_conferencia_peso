import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title='Relatório de conferência por peso', layout='centered')

# 1. INICIALIZAÇÃO
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=[
        'AL', 'Descrição', 'Volumes Tara', 'Peso Médio', 'Volumes Palete', 'Peso Bruto', 'Peso Líquido', 'Diferença'
    ])

# Título
st.markdown('<h1 style="text-align: center; font-size: 30px;">Relatório de conferência por peso</h1>', unsafe_allow_html=True)

st.write('')
st.write('')

# 2. CARREGAR DADOS
try:
    produtos_local20 = pd.read_excel('Produtos Local 20.xlsx', engine='openpyxl')
    produtos_local20['Código'] = produtos_local20['Código'].astype(str).str.strip()
    produtos_local20['Descrição'] = produtos_local20['Descrição'].astype(str).str.strip()
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
def processar_salvamento():
    # Só salva se o AL for válido
    if st.session_state.al_input != "" and descricao_al_resultado != "AL não encontrado":
        novo_registro = {
            'AL': st.session_state.al_input,
            'Descrição': descricao_al_resultado,
            'Volumes Tara': st.session_state.tara_input,
            'Peso Médio': peso_medio_kg_und,
            'Volumes Palete': st.session_state.qtd_vol_input,
            'Peso Bruto': st.session_state.peso_bruto_input,
            'Peso Líquido': peso_liquido_plt,
            'Diferença': dif_peso_palete
        }
        
        # Adiciona ao histórico
        st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo_registro])], ignore_index=True)
        
        # SINALIZADOR para mostrar a mensagem de sucesso depois do rerun
        st.session_state.salvo_com_sucesso = True
        
        # AGORA SIM, limpa os campos
        st.session_state.al_input = ""
        st.session_state.tara_input = 1
        st.session_state.peso_total_input = 0.0
        st.session_state.qtd_vol_input = 0
        st.session_state.peso_bruto_input = 0.0
    else:
        st.session_state.erro_validacao = True

# 2. O Botão agora apenas chama a função
st.button('✅ Confirmar e salvar no relatório', use_container_width=True, on_click=processar_salvamento)

# 3. Exibe as mensagens (opcional)
if st.session_state.get('salvo_com_sucesso'):
    st.success("Dados registrados e campos limpos!")
    st.session_state.salvo_com_sucesso = False # Reseta o sinalizador

if st.session_state.get('erro_validacao'):
    st.error("Por favor, insira um AL válido.")
    st.session_state.erro_validacao = False # Reseta o sinalizador

# 5. EXIBIÇÃO DA TABELA ACUMULADA
st.write("---")
st.subheader("📋 Conferências realizadas")
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
