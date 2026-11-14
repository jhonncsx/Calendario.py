import calendar
import json
import os
import uuid
from datetime import datetime, date
import streamlit as st

st.set_page_config(page_title="Calendário Financeiro 2026", layout="wide")

ARQUIVO_ANOTACOES = "anotacoes_2026.json"
CATEGORIAS = [
    "Geral", "Moradia", "Alimentação", "Transporte", "Saúde",
    "Lazer", "Educação", "Salário / Renda", "Investimentos", "Outros"
]

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

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def normalizar_item(item):
    if isinstance(item, str):
        return {
            "id": str(uuid.uuid4())[:8],
            "titulo": item[:18],
            "descricao": item,
            "tipo": "Lembrete",
            "valor": 0.0,
            "pago": False,
            "categoria": "Geral"
        }
    return {
        "id": item.get("id", str(uuid.uuid4())[:8]),
        "titulo": item.get("titulo", "Lembrete"),
        "descricao": item.get("descricao", ""),
        "tipo": item.get("tipo", "Lembrete"),
        "valor": float(item.get("valor", 0.0)),
        "pago": bool(item.get("pago", False)),
        "categoria": item.get("categoria", "Geral")
    }

def carregar_anotacoes():
    if not os.path.exists(ARQUIVO_ANOTACOES):
        return {}
    with open(ARQUIVO_ANOTACOES, "r", encoding="utf-8") as f:
        dados = json.load(f)
    resultado = {}
    for k, v in dados.items():
        if isinstance(v, list):
            resultado[k] = [normalizar_item(i) for i in v]
        else:
            resultado[k] = [normalizar_item(v)]
    return resultado

def salvar_anotacoes(dados):
    with open(ARQUIVO_ANOTACOES, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

if "anotacoes" not in st.session_state:
    st.session_state.anotacoes = carregar_anotacoes()

agora = datetime.now()

@st.dialog("Gerenciar Dia", width="large")
def abrir_modal_dia(mes, dia):
    chave = f"{mes}-{dia}"
    registros = st.session_state.anotacoes.get(chave, [])
    feriado = FERIADOS_2026.get((mes, dia))

    st.subheader(f"{dia:02d} de {MESES[mes]} de 2026")
    if feriado:
        st.info(f"Feriado Nacional: **{feriado}**")

    if registros:
        st.markdown("#### Registros salvos neste dia")
        for idx, item in enumerate(list(registros)):
            tipo_i = item["tipo"]
            val_i = item["valor"]
            pago_i = item["pago"]
            cat_i = item["categoria"]

            tag = "[Evento]"
            detalhe_val = ""
            if tipo_i == "Receita":
                tag = "[+]"
                detalhe_val = f" | **+ {brl(val_i)}** ({cat_i})"
            elif tipo_i == "Despesa":
                tag = "[-]"
                detalhe_val = f" | **- {brl(val_i)}** ({cat_i})"

            c_info, c_chk, c_del = st.columns([3.2, 1.3, 0.8])
            with c_info:
                nome = f"~~{item['titulo']}~~" if (pago_i and tipo_i != "Lembrete") else f"**{item['titulo']}**"
                st.markdown(f"{tag} {nome}{detalhe_val}")
                if item["descricao"]:
                    st.caption(item["descricao"])

            with c_chk:
                if tipo_i in ("Receita", "Despesa"):
                    rotulo = "Recebido" if tipo_i == "Receita" else "Pago"
                    marcado = st.checkbox(rotulo, value=pago_i, key=f"chk_{chave}_{item['id']}")
                    if marcado != pago_i:
                        st.session_state.anotacoes[chave][idx]["pago"] = marcado
                        salvar_anotacoes(st.session_state.anotacoes)
                        st.rerun()

            with c_del:
                if st.button("Excluir", key=f"del_{chave}_{item['id']}"):
                    st.session_state.anotacoes[chave].pop(idx)
                    if not st.session_state.anotacoes[chave]:
                        del st.session_state.anotacoes[chave]
                    salvar_anotacoes(st.session_state.anotacoes)
                    st.rerun()
        st.markdown("---")

    st.markdown("#### Adicionar Novo Registro")
    tipo = st.radio("Tipo:", ["Lembrete", "Receita", "Despesa"], horizontal=True, key=f"tp_{chave}")

    c1, c2 = st.columns([2, 1])
    with c1:
        titulo = st.text_input("Título:", placeholder="Ex: Aluguel, Salário, Luz, Médico...", key=f"ti_{chave}")
    with c2:
        valor = st.number_input("Valor (R$):", min_value=0.0, step=10.0, format="%.2f", key=f"vl_{chave}") if tipo != "Lembrete" else 0.0

    categoria = "Geral"
    pago_ini = False
    if tipo != "Lembrete":
        c3, c4 = st.columns([2, 1])
        with c3:
            idx_padrao = 7 if tipo == "Receita" else 1
            categoria = st.selectbox("Categoria:", CATEGORIAS, index=idx_padrao, key=f"ct_{chave}")
        with c4:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            pago_ini = st.checkbox("Já pago / recebido", value=False, key=f"pg_{chave}")

    descricao = st.text_area("Observações:", placeholder="Detalhes opcionais...", height=68, key=f"ds_{chave}")

    c_r1, c_r2 = st.columns([1.4, 1.6])
    with c_r1:
        repetir = st.number_input("Repetir por quantos meses?", min_value=1, max_value=13 - mes, value=1, step=1, key=f"rp_{chave}")
    with c_r2:
        numerar = False
        if repetir > 1:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            numerar = st.checkbox("Numerar parcelas (1/N)", value=True, key=f"nm_{chave}")

    b1, b2 = st.columns(2)
    with b1:
        if st.button("Adicionar Registro", type="primary", use_container_width=True):
            if titulo.strip() or descricao.strip() or valor > 0:
                base = titulo.strip() if titulo.strip() else tipo
                for i in range(int(repetir)):
                    m_alvo = mes + i
                    _, max_d = calendar.monthrange(2026, m_alvo)
                    ch_alvo = f"{m_alvo}-{min(dia, max_d)}"
                    tit_final = f"{base} ({i+1}/{int(repetir)})" if (repetir > 1 and numerar) else base
                    novo = {
                        "id": str(uuid.uuid4())[:8],
                        "titulo": tit_final,
                        "descricao": descricao.strip(),
                        "tipo": tipo,
                        "valor": float(valor) if tipo != "Lembrete" else 0.0,
                        "pago": bool(pago_ini) if (i == 0 and tipo != "Lembrete") else False,
                        "categoria": categoria if tipo != "Lembrete" else "Geral"
                    }
                    st.session_state.anotacoes.setdefault(ch_alvo, []).append(novo)
                salvar_anotacoes(st.session_state.anotacoes)
            st.query_params.clear()
            st.rerun()

    with b2:
        if st.button("Fechar Janela", use_container_width=True):
            st.query_params.clear()
            st.rerun()

# --- BARRA LATERAL ---
st.sidebar.header("Navegação e Busca")
mes_ini = int(st.query_params.get("mes", agora.month))
if not (1 <= mes_ini <= 12):
    mes_ini = agora.month

mes_escolhido = st.sidebar.selectbox(
    "Escolha o mês:",
    options=list(MESES.keys()),
    index=mes_ini - 1,
    format_func=lambda x: f"{MESES[x]} 2026"
)

busca = st.sidebar.text_input("Buscar em todo 2026:", placeholder="Ex: Aluguel, Salário, Luz...").strip().lower()
if busca:
    achados = []
    for k_d, lista in st.session_state.anotacoes.items():
        m_i, d_i = map(int, k_d.split("-"))
        for it in lista:
            if busca in f"{it['titulo']} {it['descricao']} {it['categoria']}".lower():
                achados.append((m_i, d_i, it))
    achados.sort(key=lambda x: (x[0], x[1]))
    if achados:
        st.sidebar.success(f"{len(achados)} resultado(s):")
        for m_r, d_r, it_r in achados:
            v_txt = f" ({brl(it_r['valor'])})" if it_r["valor"] > 0 else ""
            st.sidebar.markdown(f"- **{d_r:02d}/{m_r:02d}** — {it_r['titulo']}{v_txt}")
    else:
        st.sidebar.info("Nenhum registro encontrado.")

st.sidebar.markdown("---")
with st.sidebar.expander("Personalizar Cores", expanded=False):
    c_rel_bg = st.color_picker("Fundo do relógio", "#1E293B")
    c_rel_tx = st.color_picker("Texto do relógio", "#38BDF8")
    c_cab = st.color_picker("Cabeçalho do calendário", "#2563EB")
    c_dias_bg = st.color_picker("Fundo dos dias", "#FFFFFF")
    c_dias_tx = st.color_picker("Números dos dias", "#1E293B")
    c_hoje = st.color_picker("Destaque do dia atual", "#F59E0B")
    c_fer = st.color_picker("Marcação de feriados", "#0EA5E9")
    c_evt = st.color_picker("Marcação de eventos", "#8B5CF6")
    c_rec = st.color_picker("Etiqueta de Receita (+)", "#10B981")
    c_desp = st.color_picker("Etiqueta de Despesa (-)", "#EF4444")

if "dia_clicado" in st.query_params:
    try:
        d_sel = int(st.query_params["dia_clicado"])
        m_sel = int(st.query_params.get("mes", mes_escolhido))
        if 1 <= d_sel <= calendar.monthrange(2026, m_sel)[1]:
            abrir_modal_dia(m_sel, d_sel)
    except ValueError:
        st.query_params.clear()

st.markdown(
    "<style>a.celula-dia{text-decoration:none!important;transition:transform .12s,filter .12s}"
    "a.celula-dia:hover{filter:brightness(.93);transform:scale(.98)}</style>",
    unsafe_allow_html=True
)

# --- DADOS DO MÊS ---
semanas = calendar.Calendar(firstweekday=6).monthdayscalendar(2026, mes_escolhido)
cab_dias = "".join(f"<div>{d}</div>" for d in ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"])

celulas_html = ""
feriados_mes, eventos_mes, receitas_mes, despesas_mes = [], [], [], []
rec_prev = desp_prev = rec_real = desp_real = 0.0
gastos_cat = {}
alertas = []
hoje_dt = date(agora.year, agora.month, agora.day)

for semana in semanas:
    for idx, dia in enumerate(semana):
        if dia == 0:
            celulas_html += f'<div style="height:92px;background:{c_dias_bg};opacity:.4;border:1px solid rgba(0,0,0,.05);"></div>'
            continue

        eh_hoje = (agora.year == 2026 and agora.month == mes_escolhido and agora.day == dia)
        feriado = FERIADOS_2026.get((mes_escolhido, dia))
        lista = st.session_state.anotacoes.get(f"{mes_escolhido}-{dia}", [])

        if feriado:
            feriados_mes.append((dia, feriado))

        tem_rec = tem_desp = tem_evt = False
        for it in lista:
            tp, vl, pg, ct = it["tipo"], it["valor"], it["pago"], it["categoria"]
            if tp == "Receita":
                tem_rec = True
                rec_prev += vl
                if pg:
                    rec_real += vl
                receitas_mes.append((dia, it))
            elif tp == "Despesa":
                tem_desp = True
                desp_prev += vl
                if pg:
                    desp_real += vl
                despesas_mes.append((dia, it))
                gastos_cat[ct] = gastos_cat.get(ct, 0.0) + vl
                if not pg:
                    diff = (date(2026, mes_escolhido, dia) - hoje_dt).days
                    if 0 <= diff <= 3:
                        alertas.append((dia, it["titulo"], vl, diff))
            else:
                tem_evt = True
                eventos_mes.append((dia, it))

        cor_num = c_fer if feriado else ("#EF4444" if idx == 0 else c_dias_tx)
        if eh_hoje:
            est_dia = f"background:{c_hoje};color:#fff;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-weight:bold;"
        else:
            est_dia = f"color:{cor_num};font-weight:{'800' if (feriado or lista) else '600'};"

        dots = ""
        for cond, cor_d in [(feriado, c_fer), (tem_evt, c_evt), (tem_rec, c_rec), (tem_desp, c_desp)]:
            if cond:
                dots += f'<span style="width:6px;height:6px;background:{cor_d};border-radius:50%;"></span>'

        badges = ""
        for it in lista[:2]:
            tp, vl, pg = it["tipo"], it["valor"], it["pago"]
            ok = "OK " if (pg and tp != "Lembrete") else ""
            if tp == "Receita":
                bg, tx = c_rec, (f"{ok}+R${vl:,.0f}".replace(",", ".") if vl > 0 else f"{ok}{it['titulo'][:9]}")
            elif tp == "Despesa":
                bg, tx = c_desp, (f"{ok}-R${vl:,.0f}".replace(",", ".") if vl > 0 else f"{ok}{it['titulo'][:9]}")
            else:
                bg, tx = c_evt, (it["titulo"][:10] + "..." if len(it["titulo"]) > 10 else it["titulo"])
            badges += f'<div style="font-size:9px;font-weight:700;background:{bg};color:#fff;opacity:{"0.7" if pg else "1"};padding:0 4px;border-radius:3px;margin-top:2px;max-width:94%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{tx}</div>'

        if len(lista) > 2:
            badges += f'<div style="font-size:9px;font-weight:bold;opacity:.75;">+{len(lista)-2} mais</div>'

        borda = f"2px solid {c_cab}" if lista else "1px solid rgba(0,0,0,.05)"
        dicas = ([f"Feriado: {feriado}"] if feriado else []) + [f"{i['titulo']} ({brl(i['valor'])})" if i['valor'] > 0 else i['titulo'] for i in lista]
        tip = f'title="{" | ".join(dicas) if dicas else f"Dia {dia:02d}/{mes_escolhido:02d}"}"'

        celulas_html += (
            f'<a class="celula-dia" href="?mes={mes_escolhido}&dia_clicado={dia}" target="_self" {tip} '
            f'style="height:92px;background:{c_dias_bg};border:{borda};padding:3px;display:flex;flex-direction:column;align-items:center;font-size:14px;">'
            f'<span style="{est_dia}">{dia}</span>'
            f'<div style="display:flex;gap:3px;height:7px;margin-top:2px;align-items:center;">{dots}</div>'
            f'{badges}</a>'
        )

def card_lateral(titulo_box, conteudo_html, margem_inf=0):
    st.markdown(
        f'<div style="padding:15px;border-radius:12px;background:rgba(128,128,128,.08);'
        f'border:1px solid rgba(128,128,128,.2);font-family:sans-serif;margin-bottom:{margem_inf}px;">'
        f'<div style="font-weight:bold;margin-bottom:10px;text-transform:uppercase;font-size:11px;letter-spacing:1px;opacity:.85;">{titulo_box}</div>'
        f'{conteudo_html}</div>',
        unsafe_allow_html=True
    )

col_esq, col_centro, col_dir = st.columns([1.15, 2.3, 1.15], gap="medium")

with col_esq:
    html_fer = (
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid rgba(128,128,128,.15);">'
        f'<span style="width:10px;height:10px;background:{c_hoje};border-radius:50%;display:inline-block;"></span>'
        f'<span style="font-size:13px;"><strong>Hoje:</strong> {agora.strftime("%d/%m/%Y")}</span></div>'
    )
    if feriados_mes:
        for df, nf in feriados_mes:
            html_fer += f'<div style="display:flex;gap:8px;margin-top:8px;font-size:13px;"><span style="width:10px;height:10px;margin-top:4px;background:{c_fer};border-radius:50%;flex-shrink:0;"></span><span><strong>Dia {df:02d}:</strong> {nf}</span></div>'
    else:
        html_fer += '<div style="font-size:12px;opacity:.65;">Nenhum feriado nacional neste mês.</div>'
    card_lateral("Feriados do Mês", html_fer, margem_inf=16)

    html_evt = ""
    if eventos_mes:
        for de, de_dados in eventos_mes:
            desc = f"<div style='font-size:12px;opacity:.8;margin-top:2px;'>{de_dados['descricao']}</div>" if de_dados["descricao"] else ""
            html_evt += f'<div style="display:flex;gap:8px;margin-top:10px;padding-bottom:8px;border-bottom:1px solid rgba(128,128,128,.12);font-size:13px;"><span style="width:10px;height:10px;margin-top:4px;background:{c_evt};border-radius:50%;flex-shrink:0;"></span><div><strong>Dia {de:02d} — {de_dados["titulo"]}</strong>{desc}</div></div>'
    else:
        html_evt = '<div style="font-size:12px;opacity:.65;">Nenhum evento marcado.</div>'
    card_lateral("Marcações / Eventos", html_evt)

with col_centro:
    @st.fragment(run_every=1)
    def mostrar_relogio():
        t = datetime.now()
        st.markdown(
            f'<div style="background:{c_rel_bg};color:{c_rel_tx};padding:12px 20px;border-radius:12px;display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;font-family:sans-serif;">'
            f'<span style="font-size:15px;">Data: {t.strftime("%d/%m/%Y")}</span>'
            f'<span style="font-size:22px;font-weight:bold;font-family:monospace;">{t.strftime("%H:%M:%S")}</span></div>',
            unsafe_allow_html=True
        )
    mostrar_relogio()

    st.markdown(
        f'<div style="border-radius:16px;overflow:hidden;box-shadow:0 10px 25px rgba(0,0,0,.12);font-family:sans-serif;border:1px solid rgba(0,0,0,.08);">'
        f'<div style="background:{c_cab};color:#fff;padding:16px;text-align:center;"><h2 style="margin:0;font-size:24px;letter-spacing:2px;text-transform:uppercase;">{MESES[mes_escolhido]} 2026</h2></div>'
        f'<div style="display:grid;grid-template-columns:repeat(7,1fr);background:{c_cab};filter:brightness(.9);color:#fff;text-align:center;font-weight:bold;font-size:12px;padding:8px 0;">{cab_dias}</div>'
        f'<div style="display:grid;grid-template-columns:repeat(7,1fr);background:{c_dias_bg};gap:1px;">{celulas_html}</div></div>',
        unsafe_allow_html=True
    )

    for dv, tv, vv, dr in alertas:
        prazo = "VENCE HOJE!" if dr == 0 else f"Vence em {dr} dia(s) (Dia {dv:02d})"
        st.warning(f"**Conta Pendente:** {tv} — **{brl(vv)}** ({prazo})")

    saldo_p = rec_prev - desp_prev
    saldo_r = rec_real - desp_real
    c_sp = c_rec if saldo_p >= 0 else c_desp
    c_sr = c_rec if saldo_r >= 0 else c_desp

    cards_fin = [
        ("Receitas (+)", brl(rec_prev), f"Recebido: {brl(rec_real)}", c_rec, "rgba(16,185,129,.12)"),
        ("Despesas (-)", brl(desp_prev), f"Pago: {brl(desp_real)}", c_desp, "rgba(239,68,68,.12)"),
        ("Saldo Pago", brl(saldo_r), "Em caixa", c_sr, "rgba(128,128,128,.1)"),
        ("Saldo Previsto", brl(saldo_p), "Fechamento", c_sp, "rgba(128,128,128,.1)")
    ]
    cards_html = "".join(
        f'<div style="padding:10px;border-radius:12px;background:{bg};border:1px solid {cor};text-align:center;">'
        f'<div style="font-size:10px;text-transform:uppercase;font-weight:bold;opacity:.85;">{t}</div>'
        f'<div style="font-size:15px;font-weight:800;color:{cor};margin-top:3px;">{v1}</div>'
        f'<div style="font-size:10px;opacity:.75;">{v2}</div></div>'
        for t, v1, v2, cor, bg in cards_fin
    )
    st.markdown(f'<div style="margin-top:16px;display:grid;grid-template-columns:repeat(4,1fr);gap:8px;font-family:sans-serif;">{cards_html}</div>', unsafe_allow_html=True)

    with st.expander("Gráficos de Gastos e Balanço Anual 2026", expanded=False):
        t1, t2 = st.tabs(["Despesas por Categoria", "Evolução Anual 2026"])
        with t1:
            if gastos_cat:
                st.bar_chart(gastos_cat, color=c_desp)
            else:
                st.info("Lance despesas neste mês para ver o gráfico.")
        with t2:
            nomes_m = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            recs = [sum(i["valor"] for k, l in st.session_state.anotacoes.items() if int(k.split("-")[0]) == m for i in l if i["tipo"] == "Receita") for m in range(1, 13)]
            desps = [sum(i["valor"] for k, l in st.session_state.anotacoes.items() if int(k.split("-")[0]) == m for i in l if i["tipo"] == "Despesa") for m in range(1, 13)]
            st.bar_chart({"Mês": nomes_m, "Receitas": recs, "Despesas": desps}, x="Mês", y=["Receitas", "Despesas"], color=[c_rec, c_desp])

with col_dir:
    def render_lista_fin(lista, cor, sinal, rotulo_pago):
        if not lista:
            return '<div style="font-size:12px;opacity:.6;margin-bottom:10px;">Nenhum lançamento.</div>'
        out = ""
        for d_item, dados in lista:
            st_badge = f"<span style='font-size:10px;background:{c_rec};color:#fff;padding:1px 5px;border-radius:4px;margin-left:4px;'>{rotulo_pago}</span>" if dados["pago"] else "<span style='font-size:10px;opacity:.65;margin-left:4px;'>(Pendente)</span>"
            sub = f"{dados['categoria']} - {dados['descricao']}" if dados["descricao"] else dados["categoria"]
            out += (
                f'<div style="display:flex;gap:8px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid rgba(128,128,128,.12);font-size:13px;">'
                f'<span style="width:10px;height:10px;margin-top:4px;background:{cor};border-radius:50%;flex-shrink:0;"></span>'
                f'<div style="width:100%;"><div style="display:flex;justify-content:space-between;">'
                f'<span><strong>Dia {d_item:02d} — {dados["titulo"]}</strong>{st_badge}</span>'
                f'<span style="color:{cor};font-weight:700;">{sinal} {brl(dados["valor"])}</span></div>'
                f'<div style="font-size:11px;opacity:.7;">{sub}</div></div></div>'
            )
        return out

    html_fin = (
        f'<div style="font-size:11px;font-weight:800;color:{c_rec};text-transform:uppercase;margin-bottom:6px;">Entradas / Receitas</div>'
        + render_lista_fin(receitas_mes, c_rec, "+", "Recebido")
        + f'<div style="font-size:11px;font-weight:800;color:{c_desp};text-transform:uppercase;margin-top:14px;margin-bottom:6px;">Saídas / Despesas</div>'
        + render_lista_fin(despesas_mes, c_desp, "-", "Pago")
    )
    card_lateral("Movimentações Financeiras", html_fin)
