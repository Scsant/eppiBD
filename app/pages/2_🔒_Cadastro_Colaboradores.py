# app/pages/2_🔒_Cadastro_Colaboradores.py
from services.supabase_service import supabase  # ✅ correto!
import streamlit as st
import pandas as pd
from postgrest.exceptions import APIError
from services.supabase_service import (
    listar_colaboradores,
    inserir_colaborador,
    atualizar_colaborador,
    excluir_colaboradores
)

st.set_page_config(page_title="Cadastro de Colaboradores", layout="wide")

# 🔐 Autenticação
senha = st.text_input("Digite a senha", type="password")
if senha != "Troca@2025":
    st.error("Acesso restrito.")
    st.stop()

st.success("Acesso autorizado")


df = pd.DataFrame(listar_colaboradores())
st.write(f"🔢 Total de colaboradores: {len(df)}")


st.markdown("## 🧑‍💼 Lista de Colaboradores Ativos")
if df.empty:
    st.info("Nenhum colaborador cadastrado.")
    st.stop()

# Entrada direta da matrícula
matricula_busca = st.text_input("Digite a matrícula do colaborador para editar")

if matricula_busca:
    try:
        colaborador_encontrado = df[df["matricula"] == matricula_busca].iloc[0]
        colaborador_id = colaborador_encontrado["id"]  # ✅ Aqui sim é o UUID correto

        col_data = colaborador_encontrado


        with st.form("form_edicao"):
            nome = st.text_input("Nome", value=col_data["nome"])
            matricula = st.text_input("Matrícula", value=col_data["matricula"])
            funcao = st.text_input("Função", value=col_data["funcao"])
            equipe = st.text_input("Equipe", value=col_data["equipe"])

            # Selectbox de frotas válidas
            setores_result = supabase.table("setores").select("frota").execute()
            frotas = sorted({item["frota"] for item in setores_result.data if item["frota"]})

            frota_atual = col_data.get("frota", "")  # 🔐 Proteção contra KeyError
            frota_index = frotas.index(frota_atual) if frota_atual in frotas else 0
            frota = st.selectbox("Frota", frotas, index=frota_index)

            # Apenas visual (não editável)
            st.text_input("Centro de Custo", value=col_data.get("centro_custo", ""), disabled=True)

            ativo = st.checkbox("Ativo", value=col_data.get("ativo", True))

            # ✅ Submit button corretamente dentro do formulário
            submitted = st.form_submit_button("Salvar alterações")

        if submitted:
            try:
                matricula_formatada = str(int(float(matricula.strip())))
            except ValueError:
                st.error("❌ Matrícula inválida.")
                st.stop()

            # Obter o setor_id pela frota selecionada
            novo_setor = supabase.table("setores").select("id").ilike("frota", frota.strip()).execute()
            if novo_setor.data:
                setor_id = novo_setor.data[0]["id"]

                atualizar_colaborador(
                    colaborador_id,
                    {
                        "nome": nome.strip().upper(),
                        "matricula": matricula_formatada,
                        "funcao": funcao.strip().upper(),
                        "equipe": equipe.strip().upper(),
                        "setor_id": setor_id,
                        "ativo": ativo
                    }
                )
                st.success("✅ Colaborador atualizado com sucesso.")
                st.rerun()
            else:
                st.error(f"❌ Frota '{frota}' não encontrada.")




    except IndexError:
        st.warning("Matrícula não encontrada.")





# ✅ Inserção
st.markdown("### ➕ Cadastrar Novo Colaborador")
with st.form("form_insercao"):
    nome_n = st.text_input("Nome")
    matricula_n = st.text_input("Matrícula")
    funcao_n = st.text_input("Função")
    equipe_n = st.text_input("Equipe")

    # 🧠 Busca dinâmica das frotas disponíveis
    setores_result = supabase.table("setores").select("frota").execute()
    frotas = sorted({item["frota"] for item in setores_result.data if item["frota"]})
    frota_n = st.selectbox("Frota", frotas)

    ativo_n = st.checkbox("Ativo", value=True)


    if st.form_submit_button("Cadastrar"):
        setor_data = supabase.table("setores").select("id").ilike("frota", frota_n.strip()).execute()

        if not setor_data.data:
            st.error("❌ Frota não encontrada na tabela de setores.")
            st.stop()

        setor_id = setor_data.data[0]["id"]

        try:
            matricula_formatada = str(int(float(matricula_n.strip())))
        except ValueError:
            st.error("❌ Matrícula inválida.")
            st.stop()

        novo_colaborador = {
            "nome": nome_n.strip().upper(),
            "matricula": matricula_formatada,
            "funcao": funcao_n.strip().upper(),
            "equipe": equipe_n.strip().upper(),
            "setor_id": setor_id,
            "ativo": ativo_n
        }

        try:
            inserir_colaborador(novo_colaborador)
            st.success("✅ Colaborador cadastrado com sucesso.")
            st.rerun()

        except APIError as e:
            if "duplicate key value violates unique constraint" in str(e):
                st.error(f"❌ Já existe um colaborador com a matrícula {matricula_formatada}.")
            else:
                st.error(f"❌ Erro inesperado: {e}")


st.markdown("### ❌ Excluir Colaboradores")

# 🔄 Atualiza colaboradores
colaboradores = listar_colaboradores()
df = pd.DataFrame(colaboradores)



# 🔧 Força colunas a serem string (tratamento de float em matrícula)
df["nome"] = df["nome"].astype(str)
df["matricula"] = df["matricula"].fillna("").apply(lambda x: str(int(x)) if isinstance(x, float) else str(x))

# 🔍 Campo de busca
filtro_nome = st.text_input("🔍 Buscar colaborador por nome ou matrícula:")

if filtro_nome:
    df_filtrado = df[
        df["nome"].str.contains(filtro_nome, case=False, na=False) |
        df["matricula"].str.contains(filtro_nome, na=False)
    ]
else:
    df_filtrado = df

# 🔑 Mapeia opções visíveis
mapa_exclusao = {
    f"{row['matricula']} - {row['nome']}": row["id"]
    for _, row in df_filtrado.iterrows()
}

opcoes_visiveis = list(mapa_exclusao.keys())

selecionados_visiveis = st.multiselect(
    "Selecione os colaboradores para excluir:",
    options=opcoes_visiveis
)

to_delete = [mapa_exclusao[v] for v in selecionados_visiveis]

if st.button("Excluir Selecionados") and to_delete:
    excluir_colaboradores(to_delete)
    st.success(f"✅ {len(to_delete)} colaboradores excluídos.")
    st.rerun()

