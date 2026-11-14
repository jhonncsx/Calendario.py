import calendar
import json
import os
import uuid
from datetime import datetime, date
import streamlit as st

st.set_page_config(page_title="Calendário Financeiro 2026", layout="wide")

# --- GERENCIAMENTO DE DADOS (MÚLTIPLOS REGISTROS POR DIA EM JSON) ---
ARQUIVO_ANOTACOES = "anotacoes_2026.json"

CATEGORIAS_FINANCEIRAS = [
    "Geral",
    "Moradia",
    "Alimentação",
    "Transporte",
    "Saúde",
    "Lazer",
    "Educação",
    "Salário / Renda",
    "Investimentos",
    "Outros"
]

def carregar_anotacoes():
    if os.path.exists(ARQUIVO_ANOTACOES):
        with open(ARQUIVO_ANOTACOES, "r", encoding="utf-8") as f:
            dados = json.load(f)
            convertido = {}
            for k, v in dados.items():
                if isinstance(v, list):
                    lista_norm = []
                    for item in v:
                        lista_norm.append({
                            "id": item.get("id", str(uuid.uuid4())[:8]),
                            "titulo": item.get("titulo", "Lembrete"),
                            "descricao": item.get("descricao", ""),
                            "tipo": item.get("tipo", "Lembrete"),
                            "valor": float(item.get("valor", 0.0)),
                            "pago": bool(item.get("pago", False)),
                            "categoria": item.get("categoria", "Geral")
                        })
                    convertido[k] = lista_norm
                elif isinstance(v, dict):
                    convertido[k] = [{
                        "id": v.get("id", str(uuid.uuid4())[:8]),
                        "titulo": v.get("titulo", "Lembrete"),
                        "descricao": v.get("descricao", ""),
                        "tipo": v.get("tipo", "Lembrete"),
                        "valor": float(v.get("valor", 0.0)),
                        "pago": bool(v.get("pago", False)),
                        "categoria": v.get("categoria", "Geral")
                    }]
                elif isinstance(v, str):
                    convertido[k] = [{
                        "id": str(uuid.uuid4())[:8],
                        "titulo": v[:18],
                        "descricao": v,
                        "tipo": "Lembrete",
                        "valor": 0.0,
                        "pago": False,
                        "categoria": "Geral"
                    }]
            return convertido
    return {}

def salvar_anotacoes(dados):
    with open(ARQUIVO_ANOTACOES, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

if "anotacoes" not in st.session_state:
    st.session_state.anotacoes = carregar_anotacoes()

# --- FERIADOS NACIONAIS 2026 ---
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

# --- JANELA MODAL: MÚLTIPLOS REGISTROS, RECORRÊNCIA E STATUS PAGO ---
@st.dialog("📌 Gerenciar Dia", width="large")
def abrir_modal_dia(mes, dia):
    chave_data = f"{mes}-{dia}"
    registros_dia = st.session_state.anotacoes.get(chave_data, [])
    feriado_dia = FERIADOS_2026.get((mes, dia))

    st.subheader(f"{dia:02d} de {meses_nomes[mes]} de 2026")
    if feriado_dia:
        st.info(f"🎉 Feriado Nacional: **{feriado_dia}**")

    # 1. Lista de registros já existentes no dia
    if registros_dia:
        st.markdown("#### 📋 Registros salvos neste dia")
        for idx, item in enumerate(list(registros_dia)):
            tipo_i = item.get("tipo", "Lembrete")
            val_i = float(item.get("valor", 0.0))
            pago_i = bool(item.get("pago", False))
            cat_i = item.get("categoria", "Geral")

            icone = "📌"
            extra_txt = ""
            if tipo_i == "Receita":
                icone =
