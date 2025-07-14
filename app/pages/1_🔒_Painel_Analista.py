import streamlit as st
import pandas as pd
from io import BytesIO
from services.supabase_service import listar_colaboradores_com_detalhes, listar_solicitacoes, excluir_por_ids, limpar_todas_solicitacoes, listar_requisicoes_sap_agrupadas, listar_epi_por_equipe_formatado
import io

st.set_page_config(page_title="Painel do Analista", layout="wide")

# 🔐 Autenticação
senha = st.text_input("Digite a senha", type="password")
if senha != "Gabi2906#":
    st.error("Acesso restrito.")
    st.stop()

st.success("Acesso autorizado")

solicitacoes = listar_solicitacoes()

if not solicitacoes:
    st.info("Nenhuma solicitação encontrada.")
    st.stop()

df = pd.DataFrame(solicitacoes)
df.set_index("id", inplace=True)  # 👈 importantíssimo aqui


# ✅ Adiciona a coluna antes de qualquer exibição
df["Selecionar"] = False




st.markdown("### 📋 Solicitações Pendentes para Aprovação")

# ✅ Marcar todos
select_all = st.checkbox("Selecionar todas as solicitações")
if select_all:
    df["Selecionar"] = True

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
        st.rerun()




with st.sidebar:
    st.markdown("### 📤 Exportações Especiais")
    if st.button("📥 Exportar para Excel"):
        buffer = BytesIO()
        df_export = df.drop(columns=["Selecionar"])
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, index=True)
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
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_sap.to_excel(writer, index=False)
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
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_unificado.to_excel(writer, index=False)
            buffer.seek(0)
            st.download_button(
                label="⬇️ Clique para baixar",
                data=buffer,
                file_name="colaboradores_unificados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Nenhum dado disponível.")

# Após as ações principais (após col2):
st.markdown("---")
if st.button("🔍 Ver EPIs por Equipe (Carregamento)"):
    dados_epi_equipe = listar_epi_por_equipe_formatado()
    if dados_epi_equipe:
        df_epi_equipe = pd.DataFrame(dados_epi_equipe)
        st.dataframe(df_epi_equipe, use_container_width=True)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_epi_equipe.to_excel(writer, index=False)
        buffer.seek(0)
        st.download_button(
            label="📄 Baixar Excel (EPIs Carregamento)",
            data=buffer,
            file_name="epis_por_equipe.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Nenhum dado encontrado na view vw_epi_por_equipe_formatado.")
