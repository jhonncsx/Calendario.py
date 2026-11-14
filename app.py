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
@st.dialog("Gerenciar Dia", width="large")
def abrir_modal_dia(mes, dia):
    chave_data = f"{mes}-{dia}"
    registros_dia = st.session_state.anotacoes.get(chave_data, [])
    feriado_dia = FERIADOS_2026.get((mes, dia))

    st.subheader(f"{dia:02d} de {meses_nomes[mes]} de 2026")
    if feriado_dia:
        st.info(f"Feriado Nacional: **{feriado_dia}**")

    # 1. Lista de registros já existentes no dia
    if registros_dia:
        st.markdown("#### Registros salvos neste dia")
        for idx, item in enumerate(list(registros_dia)):
            tipo_i = item.get("tipo", "Lembrete")
            val_i = float(item.get("valor", 0.0))
            pago_i = bool(item.get("pago", False))
            cat_i = item.get("categoria", "Geral")

            icone = "[Evento]"
            extra_txt = ""
            if tipo_i == "Receita":
                icone = "[+]"
                extra_txt = f" | **+ {formatar_brl(val_i)}** ({cat_i})"
            elif tipo_i == "Despesa":
                icone = "[-]"
                extra_txt = f" | **- {formatar_brl(val_i)}** ({cat_i})"

            col_info, col_check, col_del = st.columns([3.2, 1.3, 0.7])
            with col_info:
                titulo_exib = f"~~{item['titulo']}~~" if (pago_i and tipo_i in ["Receita", "Despesa"]) else f"**{item['titulo']}**"
                st.markdown(f"{icone} {titulo_exib}{extra_txt}")
                if item.get("descricao"):
                    st.caption(item["descricao"])

            with col_check:
                if tipo_i in ["Receita", "Despesa"]:
                    label_chk = "Recebido" if tipo_i == "Receita" else "Pago"
                    novo_status = st.checkbox(label_chk, value=pago_i, key=f"chk_{chave_data}_{item['id']}")
                    if novo_status != pago_i:
                        st.session_state.anotacoes[chave_data][idx]["pago"] = novo_status
                        salvar_anotacoes(st.session_state.anotacoes)
                        st.rerun()

            with col_del:
                if st.button("Excluir", key=f"del_{chave_data}_{item['id']}", help="Excluir este registro"):
                    st.session_state.anotacoes[chave_data].pop(idx)
                    if not st.session_state.anotacoes[chave_data]:
                        del st.session_state.anotacoes[chave_data]
                    salvar_anotacoes(st.session_state.anotacoes)
                    st.rerun()

        st.markdown("---")

    # 2. Formulário para adicionar novo registro (com recorrência)
    st.markdown("#### Adicionar Novo Registro")
    tipo = st.radio(
        "Tipo:",
        options=["Lembrete", "Receita", "Despesa"],
        horizontal=True,
        key=f"novo_tipo_{chave_data}"
    )

    c1, c2 = st.columns([2, 1])
    with c1:
        titulo = st.text_input(
            "Título:",
            placeholder="Ex: Aluguel, Salário, Internet, Dentista...",
            key=f"novo_tit_{chave_data}"
        )
    with c2:
        valor = 0.0
        if tipo in ["Receita", "Despesa"]:
            valor = st.number_input(
                "Valor (R$):",
                min_value=0.0,
                step=10.0,
                format="%.2f",
                key=f"novo_val_{chave_data}"
            )

    categoria = "Geral"
    pago_inicial = False
    if tipo in ["Receita", "Despesa"]:
        c3, c4 = st.columns([2, 1])
        with c3:
            categoria = st.selectbox(
                "Categoria:",
                options=CATEGORIAS_FINANCEIRAS,
                index=7 if tipo == "Receita" else 1,
                key=f"novo_cat_{chave_data}"
            )
        with c4:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            pago_inicial = st.checkbox(
                "Já pago / recebido",
                value=False,
                key=f"novo_pago_{chave_data}"
            )

    descricao = st.text_area(
        "Descrição / Observações:",
        placeholder="Detalhes opcionais...",
        height=70,
        key=f"novo_desc_{chave_data}"
    )

    # Recorrência / Parcelamento
    c_rec1, c_rec2 = st.columns([1.4, 1.6])
    with c_rec1:
        repetir_meses = st.number_input(
            "Repetir por quantos meses? (1 = só este mês):",
            min_value=1,
            max_value=12 - mes + 1,
            value=1,
            step=1,
            key=f"novo_rep_{chave_data}"
        )
    with c_rec2:
        numerar_parcelas = False
        if repetir_meses > 1:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            numerar_parcelas = st.checkbox(
                "Numerar parcelas (ex: 1/3, 2/3...)",
                value=True,
                key=f"novo_parc_{chave_data}"
            )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Adicionar Registro", type="primary", use_container_width=True):
            if titulo.strip() or descricao.strip() or valor > 0:
                base_titulo = titulo.strip() if titulo.strip() else tipo
                for i in range(int(repetir_meses)):
                    mes_alvo = mes + i
                    if mes_alvo > 12:
                        break
                    _, max_d_alvo = calendar.monthrange(2026, mes_alvo)
                    dia_alvo = min(dia, max_d_alvo)
                    chave_alvo = f"{mes_alvo}-{dia_alvo}"

                    titulo_final = f"{base_titulo} ({i + 1}/{int(repetir_meses)})" if (repetir_meses > 1 and numerar_parcelas) else base_titulo
                    novo_item = {
                        "id": str(uuid.uuid4())[:8],
                        "titulo": titulo_final,
                        "descricao": descricao.strip(),
                        "tipo": tipo,
                        "valor": float(valor) if tipo in ["Receita", "Despesa"] else 0.0,
                        "pago": bool(pago_inicial) if (i == 0 and tipo in ["Receita", "Despesa"]) else False,
                        "categoria": categoria if tipo in ["Receita", "Despesa"] else "Geral"
                    }
                    st.session_state.anotacoes.setdefault(chave_alvo, []).append(novo_item)

                salvar_anotacoes(st.session_state.anotacoes)
            st.query_params.clear()
            st.rerun()

    with col_btn2:
        if st.
