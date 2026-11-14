import calendar
import json
import os
from datetime import datetime, date
import streamlit as st

st.set_page_config(page_title="Calendário Financeiro 2026", layout="wide")

# --- GERENCIAMENTO DE ANOTAÇÕES E FINANÇAS (JSON LOCAL) ---
ARQUIVO_ANOTACOES = "anotacoes_2026.json"

def carregar_anotacoes():
    if os.path.exists(ARQUIVO_ANOTACOES):
        with open(ARQUIVO_ANOTACOES, "r", encoding="utf-8") as f:
            dados = json.load(f)
            convertido = {}
            for k, v in dados.items():
                if isinstance(v, str):
                    convertido[k] = {
                        "titulo": v[:15],
                        "descricao": v,
                        "tipo": "Lembrete",
                        "valor": 0.0
                    }
                else:
                    convertido[k] = {
                        "titulo": v.get("titulo", "Lembrete"),
                        "descricao": v.get("descricao", ""),
                        "tipo": v.get("tipo", "Lembrete"),
                        "valor": float(v.get("valor", 0.0))
                    }
            return convertido
    return {}

def salvar_anotacoes(dados):
    with open(ARQUIVO_ANOTACOES, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
@st.dialog("📌 Registro do Dia")
def abrir_modal_anotacao(mes, dia):
    chave_data = f"{mes}-{dia}"
    nota_atual = st.session_state.anotacoes.get(
        chave_data, {"titulo": "", "descricao": "", "tipo": "Lembrete", "valor": 0.0}
    )
    feriado_dia = FERIADOS_2026.get((mes, dia))

    st.subheader(f"{dia:02d} de {meses_nomes[mes]} de 2026")
    if feriado_dia:
        st.info(f"🎉 Feriado Nacional: **{feriado_dia}**")

    opcoes_tipo = ["Lembrete", "Receita", "Despesa"]
    tipo_atual = nota_atual.get("tipo", "Lembrete")
    idx_tipo = opcoes_tipo.index(tipo_atual) if tipo_atual in opcoes_tipo else 0

    tipo = st.radio(
        "Categoria do registro:",
        options=opcoes_tipo,
        index=idx_tipo,
        horizontal=True
    )

    titulo = st.text_input(
        "Título / Descrição curta:",
        value=nota_atual.get("titulo", ""),
        placeholder="Ex: Salário, Conta de Luz, Aluguel, Reunião..."
    )

    valor = 0.0
    if tipo in ["Receita", "Despesa"]:
        valor = st.number_input(
            "Valor (R$):",
            min_value=0.0,
            value=float(nota_atual.get("valor", 0.0)),
            step=10.0,
            format="%.2f"
        )

    descricao = st.text_area(
        "Observações / Detalhes:",
        value=nota_atual.get("descricao", ""),
        placeholder="Ex: Banco Nubank, código de barras, parcela 2/5...",
        height=90
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Salvar", type="primary", use_container_width=True):
            if titulo.strip() or descricao.strip() or valor > 0:
                titulo_final = titulo.strip() if titulo.strip() else tipo
                st.session_state.anotacoes[chave_data] = {
                    "titulo": titulo_final,
                    "descricao": descricao.strip(),
                    "tipo": tipo,
                    "valor": float(valor) if tipo in ["Receita", "Despesa"] else 0.0
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

st.sidebar.caption("💡 Clique em qualquer dia para lançar receitas, despesas ou eventos.")

st.sidebar.markdown("---")
with st.sidebar.expander("🎨 Personalizar Cores", expanded=False):
    cor_fundo_relogio = st.color_picker("Fundo do relógio", "#1E293B")
    cor_texto_relogio = st.color_picker("Texto do relógio", "#38BDF8")
    cor_cabecalho = st.color_picker("Cabeçalho do calendário", "#2563EB")
    cor_fundo_dias = st.color_picker("Fundo dos dias", "#FFFFFF")
    cor_texto_dias = st.color_picker("Números dos dias", "#1E293B")
    cor_destaque_hoje = st.color_picker("Destaque do dia atual", "#F59E0B")
    cor_feriado = st.color_picker("Marcação de feriados", "#0EA5E9")
    cor_nota = st.color_picker("Marcação de eventos", "#8B5CF6")
    cor_receita = st.color_picker("Etiqueta de Receita (+)", "#10B981")
    cor_despesa = st.color_picker("Etiqueta de Despesa (-)", "#EF4444")

# --- VERIFICA SE ALGUM DIA FOI CLICADO ---
if "dia_clicado" in st.query_params:
    try:
        dia_sel = int(st.query_params["dia_clicado"])
        mes_sel = int(st.query_params.get("mes", mes_escolhido))
        _, max_dias = calendar.monthrange(2026, mes_sel)
        if 1 <= dia_sel <= max_dias:
            abrir_modal_anotacao(mes_sel, dia_sel)
    except ValueError:
        st.query_params.clear()

# --- CSS HOVER ---
st.markdown(
    """
    <style>
    a.celula-dia {
        text-decoration: none !important;
        transition: transform 0.12s ease, filter 0.12s ease;
    }
    a.celula-dia:hover {
        filter: brightness(0.93);
        transform: scale(0.98);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- PROCESSAMENTO DOS DADOS DO MÊS ---
cal = calendar.Calendar(firstweekday=6)
semanas = cal.monthdayscalendar(2026, mes_escolhido)
dias_semana = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]

cabecalho_dias_html = "".join(f"<div>{dia}</div>" for dia in dias_semana)

celulas_html = ""
feriados_do_mes = []
eventos_do_mes = []
receitas_do_mes = []
despesas_do_mes = []

total_receitas = 0.0
total_despesas = 0.0
alertas_vencimento = []
hoje_date = date(agora.year, agora.month, agora.day)

for semana in semanas:
    for idx, dia in enumerate(semana):
        if dia == 0:
            celulas_html += (
                f'<div style="height: 88px; background-color: {cor_fundo_dias}; '
                f'opacity: 0.4; border: 1px solid rgba(0,0,0,0.05);"></div>'
            )
        else:
            eh_hoje = (agora.year == 2026 and agora.month == mes_escolhido and agora.day == dia)
            nome_feriado = FERIADOS_2026.get((mes_escolhido, dia))
            nota_dia = st.session_state.anotacoes.get(f"{mes_escolhido}-{dia}")

            if nome_feriado:
                feriados_do_mes.append((dia, nome_feriado))

            cor_etiqueta = cor_nota
            if nota_dia:
                tipo_reg = nota_dia.get("tipo", "Lembrete")
                valor_reg = float(nota_dia.get("valor", 0.0))

                if tipo_reg == "Receita":
                    cor_etiqueta = cor_receita
                    total_receitas += valor_reg
                    receitas_do_mes.append((dia, nota_dia))
                elif tipo_reg == "Despesa":
                    cor_etiqueta = cor_despesa
                    total_despesas += valor_reg
                    despesas_do_mes.append((dia, nota_dia))

                    data_venc = date(2026, mes_escolhido, dia)
                    dias_restantes = (data_venc - hoje_date).days
                    if 0 <= dias_restantes <= 3:
                        alertas_vencimento.append((dia, nota_dia["titulo"], valor_reg, dias_restantes))
                else:
                    eventos_do_mes.append((dia, nota_dia))

            if nome_feriado:
                cor_numero = cor_feriado
            elif idx == 0:
                cor_numero = "#EF4444"
            else:
                cor_numero = cor_texto_dias

            if eh_hoje:
                estilo_dia = (
                    f"background-color: {cor_destaque_hoje}; color: #FFFFFF; border-radius: 50%; "
                    f"width: 28px; height: 28px; display: flex; align-items: center; "
                    f"justify-content: center; font-weight: bold;"
                )
            else:
                estilo_dia = f"color: {cor_numero}; font-weight: {'800' if (nome_feriado or nota_dia) else '600'};"

            bolinhas = ""
            if nome_feriado:
                bolinhas += f'<span style="width: 6px; height: 6px; background-color: {cor_feriado}; border-radius: 50%;"></span>'
            if nota_dia:
                bolinhas += f'<span style="width: 6px; height: 6px; background-color: {cor_etiqueta}; border-radius: 50%;"></span>'

            indicadores_html = (
                f'<div style="display: flex; gap: 4px; height: 7px; margin-top: 3px; align-items: center;">'
                f'{bolinhas}</div>'
            )

            previa_nota = ""
            if nota_dia:
                tipo_reg = nota_dia.get("tipo", "Lembrete")
                valor_reg = float(nota_dia.get("valor", 0.0))
                if tipo_reg in ["Receita", "Despesa"] and valor_reg > 0:
                    sinal = "+" if tipo_reg == "Receita" else "-"
                    texto_badge = f"{sinal} R${valor_reg:,.0f}".replace(",", ".")
                else:
                    texto_badge = nota_dia["titulo"][:10] + "…" if len(nota_dia["titulo"]) > 10 else nota_dia["titulo"]

                previa_nota = (
                    f'<div style="font-size: 10px; font-weight: 700; background-color: {cor_etiqueta}; color: #FFFFFF; '
                    f'padding: 1px 5px; border-radius: 4px; margin-top: 3px; max-width: 92%; '
                    f'white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{texto_badge}</div>'
                )

            borda_celula = f"2px solid {cor_etiqueta}" if nota_dia else "1px solid rgba(0,0,0,0.05)"

            textos_tooltip = [f"Clique para editar dia {dia:02d}/{mes_escolhido:02d}"]
            if nome_feriado:
                textos_tooltip.insert(0, f"Feriado: {nome_feriado}")
            if nota_dia:
                val_str = f" ({formatar_brl(nota_dia['valor'])})" if nota_dia.get("valor", 0) > 0 else ""
                textos_tooltip.insert(0, f"[{nota_dia.get('tipo', 'Lembrete')}] {nota_dia['titulo']}{val_str}")
            tooltip = f'title="{" | ".join(textos_tooltip)}"'

            celulas_html += (
                f'<a class="celula-dia" href="?mes={mes_escolhido}&dia_clicado={dia}" target="_self" {tooltip} '
                f'style="height: 88px; background-color: {cor_fundo_dias}; '
                f'border: {borda_celula}; padding: 3px; display: flex; '
                f'flex-direction: column; align-items: center; justify-content: center; font-size: 15px; '
                f'cursor: pointer;">'
                f'<span style="{estilo_dia}">{dia}</span>'
                f'{indicadores_html}'
                f'{previa_nota}'
                f'</a>'
            )

# --- LAYOUT EM 3 COLUNAS: ESQUERDA (FERIADOS E EVENTOS) | CENTRO (CALENDÁRIO) | DIREITA (FINANÇAS) ---
col_esq, col_centro, col_dir = st.columns([1.15, 2.3, 1.15], gap="medium")

# ==================== COLUNA ESQUERDA ====================
with col_esq:
    # Card 1: Feriados do Mês
    itens_feriados = (
        f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid rgba(128,128,128,0.15);">'
        f'<span style="width: 10px; height: 10px; background-color: {cor_destaque_hoje}; border-radius: 50%; display: inline-block; flex-shrink: 0;"></span>'
        f'<span style="font-size: 13px;"><strong>Hoje:</strong> {agora.strftime("%d/%m/%Y")}</span>'
        f'</div>'
    )

    if feriados_do_mes:
        for dia_f, nome_f in feriados_do_mes:
            itens_feriados += (
                f'<div style="display: flex; align-items: flex-start; gap: 8px; margin-top: 8px;">'
                f'<span style="width: 10px; height: 10px; margin-top: 4px; background-color: {cor_feriado}; border-radius: 50%; display: inline-block; flex-shrink: 0;"></span>'
                f'<span style="font-size: 13px; line-height: 1.3;"><strong>Dia {dia_f:02d}:</strong> {nome_f}</span>'
                f'</div>'
            )
    else:
        itens_feriados += '<div style="font-size: 12px; opacity: 0.65;">Nenhum feriado nacional neste mês.</div>'

    st.markdown(
        f'<div style="padding: 15px; border-radius: 12px; background-color: rgba(128, 128, 128, 0.08); '
        f'border: 1px solid rgba(128, 128, 128, 0.2); font-family: sans-serif; margin-bottom: 16px;">'
        f'<div style="font-weight: bold; margin-bottom: 10px; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; opacity: 0.85;">🎉 Feriados do Mês</div>'
        f'{itens_feriados}'
        f'</div>',
        unsafe_allow_html=True
    )

    # Card 2: Marcações / Eventos
    itens_eventos = ""
    if eventos_do_mes:
        for dia_e, dados_e in eventos_do_mes:
            desc_e = f"<div style='font-size: 12px; opacity: 0.8; margin-top: 2px;'>{dados_e['descricao']}</div>" if dados_e["descricao"] else ""
            itens_eventos += (
                f'<div style="display: flex; align-items: flex-start; gap: 8px; margin-top: 10px; padding-bottom: 8px; border-bottom: 1px solid rgba(128,128,128,0.12);">'
                f'<span style="width: 10px; height: 10px; margin-top: 4px; background-color: {cor_nota}; border-radius: 50%; display: inline-block; flex-shrink: 0;"></span>'
                f'<div style="font-size: 13px; line-height: 1.3;">'
                f'<strong>Dia {dia_e:02d} — {dados_e["titulo"]}</strong>'
                f'{desc_e}'
                f'</div>'
                f'</div>'
            )
    else:
        itens_eventos = '<div style="font-size: 12px; opacity: 0.65;">Nenhum evento ou lembrete marcado.</div>'

    st.markdown(
        f'<div style="padding: 15px; border-radius: 12px; background-color: rgba(128, 128, 128, 0.08); '
        f'border: 1px solid rgba(128, 128, 128, 0.2); font-family: sans-serif;">'
        f'<div style="font-weight: bold; margin-bottom: 8px; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; opacity: 0.85;">📌 Marcações / Eventos</div>'
        f'{itens_eventos}'
        f'</div>',
        unsafe_allow_html=True
    )

# ==================== COLUNA CENTRAL ====================
with col_centro:
    @st.fragment(run_every=1)
    def mostrar_relogio():
        tempo_atual = datetime.now()
        data_str = tempo_atual.strftime("%d/%m/%Y")
        hora_str = tempo_atual.strftime("%H:%M:%S")
        html_relogio = (
            f'<div style="background-color: {cor_fundo_relogio}; color: {cor_texto_relogio}; '
            f'padding: 12px 20px; border-radius: 12px; display: flex; justify-content: space-between; '
            f'align-items: center; margin-bottom: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); font-family: sans-serif;">'
            f'<span style="font-size: 15px; opacity: 0.9;">📅 {data_str}</span>'
            f'<span style="font-size: 22px; font-weight: bold; font-family: monospace;">⏰ {hora_str}</span>'
            f'</div>'
        )
        st.markdown(html_relogio, unsafe_allow_html=True)

    mostrar_relogio()

    html_calendario = (
        f'<div style="border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.12); '
        f'font-family: sans-serif; border: 1px solid rgba(0,0,0,0.08);">'
        f'<div style="background-color: {cor_cabecalho}; color: #FFFFFF; padding: 16px; text-align: center;">'
        f'<h2 style="margin: 0; font-size: 24px; letter-spacing: 2px; text-transform: uppercase;">{meses_nomes[mes_escolhido]} 2026</h2>'
        f'</div>'
        f'<div style="display: grid; grid-template-columns: repeat(7, 1fr); background-color: {cor_cabecalho}; '
        f'filter: brightness
