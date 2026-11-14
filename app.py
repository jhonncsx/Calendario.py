import calendar
import json
import os
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="Calendário 2026", layout="centered")

# --- GERENCIAMENTO DE ANOTAÇÕES (ARQUIVO JSON LOCAL) ---
ARQUIVO_ANOTACOES = "anotacoes_2026.json"

def carregar_anotacoes():
    if os.path.exists(ARQUIVO_ANOTACOES):
        with open(ARQUIVO_ANOTACOES, "r", encoding="utf-8") as f:
            dados = json.load(f)
            convertido = {}
            for k, v in dados.items():
                if isinstance(v, str):
                    convertido[k] = {"titulo": v[:15], "descricao": v}
                else:
                    convertido[k] = v
            return convertido
    return {}

def salvar_anotacoes(dados):
    with open(ARQUIVO_ANOTACOES, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

if "anotacoes" not in st.session_state:
    st.session_state.anotacoes = carregar_anotacoes()

# --- DICIONÁRIO DE FERIADOS NACIONAIS 2026 ---
FERIADOS_2026 = {
    (1, 1): "Confraternização Universal (Ano Novo)",
    (2, 16): "Carnaval (Ponto Facultativo)",
    (2, 17): "Carnaval",
    (2, 18): "Quarta-feira de Cinzas (Ponto Facultativo até 14h)",
    (4, 3): "Sexta-feira Santa (Paixão de Cristo)",
    (4, 21): "Tiradentes",
    (5, 1): "Dia Mundial do Trabalho",
    (6, 4): "Corpus Christi (Ponto Facultativo)",
    (9, 7): "Independência do Brasil",
    (10, 12): "Nossa Senhora Aparecida",
    (11, 2): "Finados",
    (11, 15): "Proclamação da República",
    (11, 20): "Dia Nacional de Zumbi e da Consciência Negra",
    (12, 25): "Natal"
}

meses_nomes = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

agora = datetime.now()

# --- JANELA MODAL (POP-UP) AO CLICAR NO DIA ---
@st.dialog("📌 Lembrete do Dia")
def abrir_modal_anotacao(mes, dia):
    chave_data = f"{mes}-{dia}"
    nota_atual = st.session_state.anotacoes.get(chave_data, {"titulo": "", "descricao": ""})
    feriado_dia = FERIADOS_2026.get((mes, dia))

    st.subheader(f"{dia:02d} de {meses_nomes[mes]} de 2026")
    if feriado_dia:
        st.info(f"🎉 Feriado Nacional: **{feriado_dia}**")

    titulo = st.text_input(
        "Título da marcação:",
        value=nota_atual.get("titulo", ""),
        placeholder="Ex: Reunião, Prova, Médico, Aniversário..."
    )

    descricao = st.text_area(
        "Descrição / Detalhes:",
        value=nota_atual.get("descricao", ""),
        placeholder="Escreva aqui os detalhes que deseja lembrar...",
        height=120
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Salvar", type="primary", use_container_width=True):
            if titulo.strip() or descricao.strip():
                titulo_final = titulo.strip() if titulo.strip() else "Lembrete"
                desc_final = descricao.strip()
                st.session_state.anotacoes[chave_data] = {
                    "titulo": titulo_final,
                    "descricao": desc_final
                }
                salvar_anotacoes(st.session_state.anotacoes)
            st.query_params.clear()
            st.rerun()

    with col2:
        if st.button("🗑️ Excluir", use_container_width=True):
            if chave_data in st.session_state.anotacoes:
                del st.session_state.anotacoes[chave_data]
                salvar_anotacoes(st.session_state.anotacoes)
            st.query_params.clear()
            st.rerun()

# --- BARRA LATERAL ---
st.sidebar.header("Navegação e Cores")

mes_inicial = int(st.query_params.get("mes", agora.month))
if not (1 <= mes_inicial <= 12):
    mes_inicial = agora.month

mes_escolhido = st.sidebar.selectbox(
    "Escolha o mês:",
    options=list(meses_nomes.keys()),
    index=mes_inicial - 1,
    format_func=lambda x: f"{meses_nomes[x]} 2026"
)

st.sidebar.caption("💡 Dica: Clique diretamente sobre qualquer dia no calendário para adicionar ou editar um lembrete.")

st.sidebar.markdown("---")
with st.sidebar.expander("🎨 Personalizar Cores", expanded=True):
    cor_fundo_relogio = st.color_picker("Fundo do relógio", "#1E293B")
    cor_texto_relogio = st.color_picker("Texto do relógio", "#38BDF8")
    cor_cabecalho = st.color_picker("Cabeçalho do calendário", "#2563EB")
    cor_fundo_dias = st.color_picker("Fundo dos dias", "#FFFFFF")
    cor_texto_dias = st.color
