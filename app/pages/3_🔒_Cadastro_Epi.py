import streamlit as st
import pandas as pd
from postgrest.exceptions import APIError
from services.supabase_service import (
    listar_categorias_epis,
    inserir_epi,
    atualizar_epi,
    excluir_epi,
    supabase
)

st.set_page_config(page_title="Cadastro de EPIs", layout="wide")

# 🔐 Autenticação
senha = st.text_input("Digite a senha", type="password")
if senha != "Gabi2906#":
    st.error("Acesso restrito.")
    st.stop()

st.success("Acesso autorizado")

# Listar EPIs já cadastrados
epis_result = supabase.table("epis").select("*").order("nome").execute()
df = pd.DataFrame(epis_result.data)
st.write(f"🔢 Total de EPIs: {len(df)}")

st.markdown("## 🧰 Lista de EPIs Cadastrados")
if df.empty:
    st.info("Nenhum EPI cadastrado.")
else:
    st.dataframe(df, use_container_width=True)

# --- Edição de EPI ---
st.markdown("### ✏️ Editar EPI")
if not df.empty:
    epi_opcoes = {f"{row['nome']} ({row['codigo_sap']})": row['id'] for _, row in df.iterrows()}
    epi_selecionado = st.selectbox("Selecione o EPI para editar", ["-"] + list(epi_opcoes.keys()))
    if epi_selecionado != "-":
        epi_id = epi_opcoes[epi_selecionado]
        epi_data = df[df['id'] == epi_id].iloc[0]
        with st.form("form_edicao_epi"):
            categoria_e = st.text_input("Categoria", value=epi_data["categoria"])
            nome_e = st.text_input("Nome do EPI", value=epi_data["nome"])
            codigo_sap_e = st.text_input("Código SAP", value=epi_data["codigo_sap"])
            quantidade_permitida_e = st.number_input("Quantidade Permitida", min_value=1, value=int(epi_data["quantidade_permitida"]), step=1)
            ativo_e = st.checkbox("Ativo", value=epi_data["ativo"])
            if st.form_submit_button("Salvar alterações"):
                epi_editado = {
                    "categoria": categoria_e.strip(),
                    "nome": nome_e.strip(),
                    "codigo_sap": codigo_sap_e.strip(),
                    "quantidade_permitida": quantidade_permitida_e,
                    "ativo": ativo_e
                }
                try:
                    atualizar_epi(epi_id, epi_editado)
                    st.success("✅ EPI atualizado com sucesso.")
                    st.rerun()
                except APIError as e:
                    if "duplicate key value violates unique constraint" in str(e):
                        st.error(f"❌ Já existe um EPI com o código SAP {codigo_sap_e}.")
                    else:
                        st.error(f"❌ Erro inesperado: {e}")

# --- Exclusão de EPI ---
st.markdown("### ❌ Excluir EPI")
st.info("Atenção: Só é possível excluir EPIs que não estejam sendo utilizados em nenhuma requisição ou view. Caso contrário, será exibida uma mensagem de erro.")
if not df.empty:
    epi_opcoes_excluir = {f"{row['nome']} ({row['codigo_sap']})": row['id'] for _, row in df.iterrows()}
    epi_excluir = st.selectbox("Selecione o EPI para excluir", ["-"] + list(epi_opcoes_excluir.keys()), key="excluir_epi")
    if epi_excluir != "-":
        epi_id_excluir = epi_opcoes_excluir[epi_excluir]
        if st.button("Excluir EPI", key="btn_excluir_epi"):
            try:
                excluir_epi(epi_id_excluir)
                st.success("✅ EPI excluído com sucesso.")
                st.rerun()
            except APIError as e:
                if "foreign key constraint" in str(e).lower() or "violates foreign key constraint" in str(e).lower():
                    st.error("❌ Não é possível excluir este EPI pois ele está sendo utilizado em alguma requisição ou view. Desvincule antes de tentar novamente.")
                else:
                    st.error(f"❌ Erro inesperado: {e}")

# Formulário para cadastro de novo EPI
st.markdown("### ➕ Cadastrar Novo EPI")
with st.form("form_epi"):
    categoria = st.text_input("Categoria")
    nome = st.text_input("Nome do EPI")
    codigo_sap = st.text_input("Código SAP")
    quantidade_permitida = st.number_input("Quantidade Permitida", min_value=1, value=1, step=1)
    ativo = st.checkbox("Ativo", value=True)

    if st.form_submit_button("Cadastrar"):
        novo_epi = {
            "categoria": categoria.strip(),
            "nome": nome.strip(),
            "codigo_sap": codigo_sap.strip(),
            "quantidade_permitida": quantidade_permitida,
            "ativo": ativo
        }
        try:
            inserir_epi(novo_epi)
            st.success("✅ EPI cadastrado com sucesso.")
            st.rerun()
        except APIError as e:
            if "duplicate key value violates unique constraint" in str(e):
                st.error(f"❌ Já existe um EPI com o código SAP {codigo_sap}.")
            else:
                st.error(f"❌ Erro inesperado: {e}") 