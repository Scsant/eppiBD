# app/pages/2_🔒_Cadastro_Colaboradores.py

import streamlit as st
import pandas as pd
from services.supabase_service import (
    listar_colaboradores,
    inserir_colaborador,
    atualizar_colaborador,
    excluir_colaboradores
)

st.set_page_config(page_title="Cadastro de Colaboradores", layout="wide")

# 🔐 Autenticação
senha = st.text_input("Digite a senha", type="password")
if senha != "Gabi2906#":
    st.error("Acesso restrito.")
    st.stop()

st.success("Acesso autorizado")

# 🔄 Carregar dados
colaboradores = listar_colaboradores()
df = pd.DataFrame(colaboradores)

st.markdown("## 🧑‍💼 Lista de Colaboradores Ativos")
if df.empty:
    st.info("Nenhum colaborador cadastrado.")
    st.stop()

# Entrada direta da matrícula
matricula_busca = st.text_input("Digite a matrícula do colaborador para editar")

if matricula_busca:
    try:
        colaborador_encontrado = df[df["matricula"] == matricula_busca].iloc[0]
        row_to_edit = colaborador_encontrado.name
        col_data = df.loc[row_to_edit]

        with st.form("form_edicao"):
            nome = st.text_input("Nome", value=col_data["nome"])
            matricula = st.text_input("Matrícula", value=col_data["matricula"])
            funcao = st.text_input("Função", value=col_data["funcao"])
            equipe = st.text_input("Equipe", value=col_data["equipe"])
            frota = st.text_input("Frota", value=col_data["frota"])
            centro_custo = st.text_input("Centro de Custo", value=col_data.get("centro_custo", ""))
            ativo = st.checkbox("Ativo", value=col_data.get("ativo", True))

            if st.form_submit_button("Salvar alterações"):
                atualizar_colaborador(
                    row_to_edit,
                    {
                        "nome": nome,
                        "matricula": matricula,
                        "funcao": funcao,
                        "equipe": equipe,
                        "frota": frota,
                        "centro_custo": centro_custo,
                        "ativo": ativo
                    }
                )
                st.success("Colaborador atualizado com sucesso.")
                st.experimental_rerun()

    except IndexError:
        st.warning("Matrícula não encontrada.")



# ✅ Inserção
st.markdown("### ➕ Cadastrar Novo Colaborador")
with st.form("form_insercao"):
    nome_n = st.text_input("Nome")
    matricula_n = st.text_input("Matrícula")
    funcao_n = st.text_input("Função")
    equipe_n = st.text_input("Equipe")
    frota_n = st.text_input("Frota")
    centro_custo_n = st.text_input("Centro de Custo")
    ativo_n = st.checkbox("Ativo", value=True)

    if st.form_submit_button("Cadastrar"):
        inserir_colaborador({
            "nome": nome_n,
            "matricula": matricula_n,
            "funcao": funcao_n,
            "equipe": equipe_n,
            "frota": frota_n,
            "centro_custo": centro_custo_n,
            "ativo": ativo_n
        })
        st.success("Colaborador cadastrado com sucesso.")
        st.experimental_rerun()

# ✅ Exclusão
st.markdown("### ❌ Excluir Colaboradores")
# Mapear matrícula + nome -> id
mapa_exclusao = {
    f"{row['matricula']} - {row['nome']}": row.name
    for _, row in df.iterrows()
}

opcoes_visiveis = list(mapa_exclusao.keys())

selecionados_visiveis = st.multiselect(
    "Selecione os colaboradores para excluir:",
    options=opcoes_visiveis
)

to_delete = [mapa_exclusao[v] for v in selecionados_visiveis]

if st.button("Excluir Selecionados") and to_delete:
    excluir_colaboradores(to_delete)
    st.success(f"{len(to_delete)} colaboradores excluídos.")
    st.experimental_rerun()
