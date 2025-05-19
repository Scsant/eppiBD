# app/pages/1_🔒_Painel_Analista.py

import streamlit as st
import pandas as pd
from io import BytesIO
from services.supabase_service import listar_solicitacoes, excluir_por_ids, limpar_todas_solicitacoes

st.set_page_config(page_title="Painel do Analista", layout="wide")

# Autenticação simples
senha = st.text_input("Digite a senha", type="password")
if senha != "Gabi2906#":
    st.error("Acesso restrito.")
    st.stop()

st.success("Acesso autorizado")

# Consulta os dados
solicitacoes = listar_solicitacoes()

if not solicitacoes:
    st.info("Nenhuma solicitação encontrada.")
    st.stop()

# Agrupamento por categoria de frota
df_analise = pd.DataFrame(solicitacoes)

def classificar_frota(frota: str) -> str:
    frota = frota.lower() if frota else ""
    if "leste" in frota or "oeste" in frota:
        return "Transporte de Madeira"
    elif "carregamento" in frota:
        return "Carregamento"
    elif "pátio" in frota or "patio" in frota:
        return "Pátio de Madeira"
    return "Outros"

df_analise["categoria_frota"] = df_analise["frota"].apply(classificar_frota)
contagem = df_analise["categoria_frota"].value_counts()

# Mostrar balança por categoria
categorias = ["Transporte de Madeira", "Carregamento", "Pátio de Madeira"]
colunas = st.columns(len(categorias))

for col, categoria in zip(colunas, categorias):
    total = contagem.get(categoria, 0)
    col.metric(label=f"Solicitações - {categoria}", value=total)

# Montagem da tabela com opções
df = pd.DataFrame(solicitacoes)
df["Selecionar"] = False
df.set_index("id", inplace=True)

st.markdown("### Solicitações de EPIs")

# Marcar todos
select_all = st.checkbox("Selecionar todas as solicitações")
if select_all:
    df["Selecionar"] = True

# Seletor para múltiplas exclusões
selecionados = st.multiselect(
    "Selecione as solicitações a excluir:",
    options=df.index.tolist(),
    format_func=lambda x: f"{df.loc[x, 'nome']} - {df.loc[x, 'matricula']}"
)

# Mostrar tabela
st.dataframe(df.drop(columns=["Selecionar"]), use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("Excluir Selecionados") and selecionados:
        excluir_por_ids(selecionados)
        st.success(f"{len(selecionados)} solicitações excluídas.")
        st.experimental_rerun()

with col2:
    if st.button("Exportar para Excel"):
        buffer = BytesIO()
        df_export = df.drop(columns=["Selecionar"])
        df_export.to_excel(buffer, index=True)
        buffer.seek(0)
        st.download_button(
            label="📥 Baixar Excel",
            data=buffer,
            file_name="solicitacoes_epi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Botão para limpar base inteira
if st.button("🧹 Limpar Base Completa"):
    limpar_todas_solicitacoes()
    st.success("Base de solicitações limpa com sucesso.")
    st.experimental_rerun()
