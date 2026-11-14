import calendar
from datetime import datetime
import psycopg2
import streamlit as st

st.set_page_config(page_title="Calendário 2026", layout="centered")

# --- CONEXÃO E OPERAÇÕES COM O BANCO DE DADOS NEON (POSTGRESQL) ---
def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

def inicializar_banco():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS anotacoes_2026 (
                    chave_data VARCHAR(10) PRIMARY KEY,
                    titulo VARCHAR(100) NOT NULL,
                    descricao TEXT
                );
            """)
        conn.commit()

def carregar_anotacoes():
    inicializar_banco()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT chave_data, titulo, descricao FROM anotacoes_2026;")
            linhas = cur.fetchall()
            return {
                row[0]: {"titulo": row[1], "descricao": row[2] or ""}
                for row in linhas
            }

def salvar_anotacao_db(chave_data, titulo, descricao):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO anotacoes_2026 (chave_data, titulo, descricao)
                VALUES (%s, %s, %s)
                ON CONFLICT (chave_data)
                DO UPDATE SET titulo = EXCLUDED.titulo, descricao = EXCLUDED.descricao;
            """, (chave_data, titulo, descricao))
        conn.commit()

def excluir_anotacao_db(chave_data):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM anotacoes_2026 WHERE chave_data = %s;", (chave_data,))
        conn.commit()

if "anotacoes" not in st.session_state:
    try:
        st.session_state.anotacoes = carregar_anotacoes()
    except Exception as e:
        st.error(f"Erro ao conectar ao banco Neon: {e}")
        st.stop()

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
                salvar_anotacao_db(chave_data, titulo_final, desc_final)
                st.session_state.anotacoes[chave_data] = {
                    "titulo": titulo_final,
                    "descricao": desc_final
                }
            st.query_params.clear()
            st.rerun()

    with col2:
        if st.button("🗑️ Excluir", use_container_width=True):
            if chave_data in st.session_state.anotacoes:
                excluir_anotacao_db(chave_data)
                del st.session_state.anotacoes[chave_data]
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
st.sidebar.success("☁️ Conectado ao Neon PostgreSQL")

st.sidebar.markdown("---")
with st.sidebar.expander("🎨 Personalizar Cores", expanded=True):
    cor_fundo_relogio = st.color_picker("Fundo do relógio", "#1E293B")
    cor_texto_relogio = st.color_picker("Texto do relógio", "#38BDF8")
    cor_cabecalho = st.color_picker("Cabeçalho do calendário", "#2563EB")
    cor_fundo_dias = st.color_picker("Fundo dos dias", "#FFFFFF")
    cor_texto_dias = st.color_picker("Números dos dias", "#1E293B")
    cor_destaque_hoje = st.color_picker("Destaque do dia atual", "#F59E0B")
    cor_feriado = st.color_picker("Marcação de feriados", "#10B981")
    cor_nota = st.color_picker("Marcação de anotações", "#8B5CF6")

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

# --- RELÓGIO EM TEMPO REAL ---
@st.fragment(run_every=1)
def mostrar_relogio():
    tempo_atual = datetime.now()
    data_str = tempo_atual.strftime("%d/%m/%Y")
    hora_str = tempo_atual.strftime("%H:%M:%S")
    html_relogio = (
        f'<div style="background-color: {cor_fundo_relogio}; color: {cor_texto_relogio}; '
        f'padding: 12px 20px; border-radius: 12px; display: flex; justify-content: space-between; '
        f'align-items: center; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); font-family: sans-serif;">'
        f'<span style="font-size: 16px; opacity: 0.9;">📅 {data_str}</span>'
        f'<span style="font-size: 24px; font-weight: bold; font-family: monospace;">⏰ {hora_str}</span>'
        f'</div>'
    )
    st.markdown(html_relogio, unsafe_allow_html=True)

mostrar_relogio()

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

# --- CONSTRUÇÃO DO CALENDÁRIO ---
cal = calendar.Calendar(firstweekday=6)
semanas = cal.monthdayscalendar(2026, mes_escolhido)
dias_semana = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]

cabecalho_dias_html = "".join(f"<div>{dia}</div>" for dia in dias_semana)

celulas_html = ""
feriados_do_mes = []
notas_do_mes = []

for semana in semanas:
    for idx, dia in enumerate(semana):
        if dia == 0:
            celulas_html += (
                f'<div style="height: 85px; background-color: {cor_fundo_dias}; '
                f'opacity: 0.4; border: 1px solid rgba(0,0,0,0.05);"></div>'
            )
        else:
            eh_hoje = (agora.year == 2026 and agora.month == mes_escolhido and agora.day == dia)
            nome_feriado = FERIADOS_2026.get((mes_escolhido, dia))
            nota_dia = st.session_state.anotacoes.get(f"{mes_escolhido}-{dia}")

            if nome_feriado:
                feriados_do_mes.append((dia, nome_feriado))
            if nota_dia:
                notas_do_mes.append((dia, nota_dia))

            if nome_feriado:
                cor_numero = cor_feriado
            elif idx == 0:
                cor_numero = "#EF4444"
            else:
                cor_numero = cor_texto_dias

            if eh_hoje:
                estilo_dia = (
                    f"background-color: {cor_destaque_hoje}; color: #FFFFFF; border-radius: 50%; "
                    f"width: 32px; height: 32px; display: flex; align-items: center; "
                    f"justify-content: center; font-weight: bold;"
                )
            else:
                estilo_dia = f"color: {cor_numero}; font-weight: {'800' if (nome_feriado or nota_dia) else '600'};"

            bolinhas = ""
            if nome_feriado:
                bolinhas += f'<span style="width: 7px; height: 7px; background-color: {cor_feriado}; border-radius: 50%;"></span>'
            if nota_dia:
                bolinhas += f'<span style="width: 7px; height: 7px; background-color: {cor_nota}; border-radius: 50%;"></span>'

            indicadores_html = (
                f'<div style="display: flex; gap: 4px; height: 8px; margin-top: 4px; align-items: center;">'
                f'{bolinhas}</div>'
            )

            previa_nota = ""
            if nota_dia:
                titulo_curto = nota_dia["titulo"][:12] + "…" if len(nota_dia["titulo"]) > 12 else nota_dia["titulo"]
                previa_nota = (
                    f'<div style="font-size: 10px; font-weight: 600; background-color: {cor_nota}; color: #FFFFFF; '
                    f'padding: 1px 6px; border-radius: 4px; margin-top: 3px; max-width: 92%; '
                    f'white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{titulo_curto}</div>'
                )

            borda_celula = f"2px solid {cor_nota}" if nota_dia else "1px solid rgba(0,0,0,0.05)"

            textos_tooltip = [f"Clique para anotar no dia {dia:02d}/{mes_escolhido:02d}"]
            if nome_feriado:
                textos_tooltip.insert(0, f"Feriado: {nome_feriado}")
            if nota_dia:
                desc_tip = f": {nota_dia['descricao']}" if nota_dia["descricao"] else ""
                textos_tooltip.insert(0, f"{nota_dia['titulo']}{desc_tip}")
            tooltip = f'title="{" | ".join(textos_tooltip)}"'

            celulas_html += (
                f'<a class="celula-dia" href="?mes={mes_escolhido}&dia_clicado={dia}" target="_self" {tooltip} '
                f'style="height: 85px; background-color: {cor_fundo_dias}; '
                f'border: {borda_celula}; padding: 4px; display: flex; '
                f'flex-direction: column; align-items: center; justify-content: center; font-size: 17px; '
                f'cursor: pointer;">'
                f'<span style="{estilo_dia}">{dia}</span>'
                f'{indicadores_html}'
                f'{previa_nota}'
                f'</a>'
            )

html_calendario = (
    f'<div style="border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.12); '
    f'font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; border: 1px solid rgba(0,0,0,0.08);">'
    f'<div style="background-color: {cor_cabecalho}; color: #FFFFFF; padding: 20px; text-align: center;">'
    f'<h2 style="margin: 0; font-size: 28px; letter-spacing: 2px; text-transform: uppercase;">{meses_nomes[mes_escolhido]} 2026</h2>'
    f'</div>'
    f'<div style="display: grid; grid-template-columns: repeat(7, 1fr); background-color: {cor_cabecalho}; '
    f'filter: brightness(0.9); color: #FFFFFF; text-align: center; font-weight: bold; font-size: 13px; padding: 10px 0;">'
    f'{cabecalho_dias_html}'
    f'</div>'
    f'<div style="display: grid; grid-template-columns: repeat(7, 1fr); background-color: {cor_fundo_dias}; gap: 1px;">'
    f'{celulas_html}'
    f'</div>'
    f'</div>'
)

st.markdown(html_calendario, unsafe_allow_html=True)

# --- LEGENDA ABAIXO DO CALENDÁRIO ---
itens_legenda = (
    f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">'
    f'<span style="width: 12px; height: 12px; background-color: {cor_destaque_hoje}; border-radius: 50%; display: inline-block;"></span>'
    f'<span><strong>Dia atual</strong> ({agora.strftime("%d/%m/%Y")})</span>'
    f'</div>'
)

for dia_f, nome_f in feriados_do_mes:
    itens_legenda += (
        f'<div style="display: flex; align-items: center; gap: 8px; margin-top: 6px;">'
        f'<span style="width: 12px; height: 12px; background-color: {cor_feriado}; border-radius: 50%; display: inline-block;"></span>'
        f'<span><strong>Dia {dia_f:02d} (Feriado):</strong> {nome_f}</span>'
        f'</div>'
    )

for dia_n, dados_n in notas_do_mes:
    desc_texto = f" — {dados_n['descricao']}" if dados_n["descricao"] else ""
    itens_legenda += (
        f'<div style="display: flex; align-items: center; gap: 8px; margin-top: 6px;">'
        f'<span style="width: 12px; height: 12px; background-color: {cor_nota}; border-radius: 50%; display: inline-block;"></span>'
        f'<span><strong>Dia {dia_n:02d} ({dados_n["titulo"]}):</strong>{desc_texto if desc_texto else " Sem descrição adicional."}</span>'
        f'</div>'
    )

if not feriados_do_mes and not notas_do_mes:
    itens_legenda += (
        f'<div style="margin-top: 6px; opacity: 0.7; font-size: 13px;">'
        f'Clique em qualquer dia acima para adicionar um lembrete.'
        f'</div>'
    )

html_legenda = (
    f'<div style="margin-top: 18px; padding: 15px 20px; border-radius: 12px; '
    f'background-color: rgba(128, 128, 128, 0.08); border: 1px solid rgba(128, 128, 128, 0.2); '
    f'font-family: sans-serif; font-size: 14px;">'
    f'<div style="font-weight: bold; margin-bottom: 8px; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; opacity: 0.8;">Feriados e Anotações do Mês</div>'
    f'{itens_legenda}'
    f'</div>'
)

st.markdown(html_legenda, unsafe_allow_html=True)
