import streamlit as st
import pandas as pd
from io import BytesIO
from services.supabase_service import listar_colaboradores_com_detalhes, listar_solicitacoes, excluir_por_ids, limpar_todas_solicitacoes, listar_requisicoes_sap_agrupadas

st.set_page_config(page_title="Painel do Analista", layout="wide")

# 🔐 Autenticação
senha = st.text_input("Digite a senha", type="password")
if senha != "Gabi2906#":
    st.error("Acesso restrito.")
    st.stop()

st.success("Acesso autorizado")

# 📥 Consulta a view com JOINs
solicitacoes = listar_solicitacoes()
if not solicitacoes:
    st.info("Nenhuma solicitação encontrada.")
    st.stop()

df = pd.DataFrame(solicitacoes)

# ✅ Adiciona a coluna antes de qualquer exibição
df["Selecionar"] = False




st.markdown("### 📋 Solicitações Pendentes para Aprovação")

# ✅ Marcar todos
select_all = st.checkbox("Selecionar todas as solicitações")
if select_all:
    df["Selecionar"] = True

# ✅ Multiselect amigável
selecionados = st.multiselect(
    "Selecione as solicitações a excluir:",
    options=df.index.tolist(),
    format_func=lambda x: f"{df.loc[x, 'nome']} - {df.loc[x, 'matricula']}"
)

# ✅ Visualização final com marcação
st.dataframe(df.drop(columns=["Selecionar"]), use_container_width=True)

# 🔘 Ações
col1, col2 = st.columns(2)

with col1:
    if st.button("❌ Excluir Selecionados") and selecionados:
        excluir_por_ids(selecionados)
        st.success(f"{len(selecionados)} solicitações excluídas.")
        st.rerun()

    # 🧹 Limpar base inteira
    if st.button("🧹 Limpar Base Completa"):
        limpar_todas_solicitacoes()
        st.success("Base de solicitações limpa com sucesso.")
        st.experimental_rerun()




with st.sidebar:
    st.markdown("### 📤 Exportações Especiais")
    if st.button("📥 Exportar para Excel"):
        buffer = BytesIO()
        df_export = df.drop(columns=["Selecionar"])
        df_export.to_excel(buffer, index=True)
        buffer.seek(0)
        st.download_button(
            label="📄 Baixar Excel",
            data=buffer,
            file_name="solicitacoes_epi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if st.button("📥 Baixar/SAP"):
        dados_sap = listar_requisicoes_sap_agrupadas()
        if dados_sap:
            df_sap = pd.DataFrame(dados_sap)
            buffer = BytesIO()
            df_sap.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label="📄 Clique aqui para baixar (SAP)",
                data=buffer,
                file_name="requisicoes_sap.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Nenhuma requisição SAP encontrada.")



    st.markdown("### 📦 Baixar Base Unificada")
    if st.button("📥 Baixar Base Unificada"):
        base = listar_colaboradores_com_detalhes()
        if base:
            df_unificado = pd.DataFrame(base)
            buffer = BytesIO()
            df_unificado.to_excel(buffer, index=False)
            buffer.seek(0)
            st.download_button(
                label="⬇️ Clique para baixar",
                data=buffer,
                file_name="colaboradores_unificados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Nenhum dado disponível.")
