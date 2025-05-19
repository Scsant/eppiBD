# app/components/requisicao_form.py

import streamlit as st
from services.supabase_service import (
    buscar_colaborador_por_matricula,
    enviar_pedido_concatenado,
    listar_categorias_epis,
    colaborador_ja_solicitou_na_semana,
    listar_epis_por_categoria,
)

from datetime import datetime
from services.supabase_service import enviar_pedido_concatenado




def requisicao_form():
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://raw.githubusercontent.com/Scsant/bracc2/016a697aab43b2e1e5b8dc0d5d9855659dc8ea09/logoBracell5.png" width="600">
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## Solicitação de EPIs/Logística Florestal")
    matricula = st.text_input("Digite sua matrícula")

    if "itens_pedido" not in st.session_state:
        st.session_state.itens_pedido = []

    if matricula:
        colaborador = buscar_colaborador_por_matricula(matricula)
        if colaborador:
            st.success(f"Bem-vindo, {colaborador['nome']} ({colaborador['funcao']})")

            st.markdown("### Selecione os EPIs necessários")

            categorias = listar_categorias_epis()
            categoria_selecionada = st.selectbox("Tipo de EPI", categorias)

            epis_disponiveis = listar_epis_por_categoria(categoria_selecionada)
            nome_epi = st.selectbox("Descrição do EPI", epis_disponiveis)

            quantidade = st.number_input("Quantidade", min_value=1, step=1)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Adicionar ao Resumo"):
                    item = {
                        "tipo": categoria_selecionada,
                        "descricao": nome_epi,
                        "quantidade": quantidade
                    }
                    st.session_state.itens_pedido.append(item)
                    st.success("Item adicionado ao resumo.")

            with col2:
                if st.button("Enviar Solicitações"):
                    if colaborador_ja_solicitou_na_semana(colaborador["matricula"]):
                        st.error("Você já fez uma solicitação nesta semana. Aguarde até domingo para uma nova requisição.")
                    elif st.session_state.itens_pedido:
                        enviar_pedido_concatenado(colaborador, st.session_state.itens_pedido)
                        st.success("Solicitação enviada com sucesso!")
                        st.session_state.itens_pedido.clear()



            if st.session_state.itens_pedido:
                st.markdown("### Resumo dos Itens")
                for i, item in enumerate(st.session_state.itens_pedido):
                    st.write(f"{i+1}. {item['descricao']} ({item['tipo']}) - Quantidade: {item['quantidade']}")
        else:
            st.warning("Matrícula não encontrada.")
