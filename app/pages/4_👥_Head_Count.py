import streamlit as st
import pandas as pd
from io import BytesIO
from services.supabase_service import listar_colaboradores_com_setor

st.set_page_config(page_title="Head Count por Setor", layout="wide")

# 🔐 Autenticação
senha = st.text_input("Digite a senha", type="password")
if senha != "Gabi2906#":
    st.error("Acesso restrito.")
    st.stop()
st.success("Acesso autorizado")

# 🎯 Setores com emoji
setores = {
    "transporte de madeira": {"label": "Transporte de Madeira", "emoji": "🚛"},
    "carregamento": {"label": "Carregamento", "emoji": "🚜"},
    "pátio de madeira": {"label": "Pátio de Madeira", "emoji": "🪵"},
    "patio de madeira": {"label": "Pátio de Madeira", "emoji": "🪵"},  # fallback sem acento
}

# 📥 Consulta dados
colaboradores = listar_colaboradores_com_setor()
df = pd.DataFrame(colaboradores)

# Limpeza de dados
df["setor"] = df["setor"].fillna("não informado").str.strip().str.lower()

# 📊 Contar colaboradores por setor
contagem = df["setor"].value_counts().to_dict()

# 🎯 Cabeçalho visual com métricas
cols = st.columns(3)
for i, key in enumerate(["transporte de madeira", "carregamento", "pátio de madeira"]):
    valores_aceitos = [key, "patio de madeira"] if "pátio" in key else [key]

    total = sum(
        count for setor_val, count in contagem.items()
        if setor_val in valores_aceitos
    )

    setor_label = setores[key]["label"]
    emoji = setores[key]["emoji"]
    cols[i].metric(label=f"{emoji} {setor_label}", value=total)

# 📋 Listagem por setor
st.markdown("---")
st.markdown("### 👥 Listagem por Setor")

for key in ["transporte de madeira", "carregamento", "patio de madeira"]:
    setor_label = setores[key]["label"]
    emoji = setores[key]["emoji"]
    valores_aceitos = [key, "pátio de madeira"] if key == "patio de madeira" else [key]

    subset = df[df["setor"].isin(valores_aceitos)]

    with st.expander(f"{emoji} Lista de {setor_label} ({len(subset)})"):
        st.dataframe(subset[["nome", "matricula", "funcao", "equipe", "setor"]], use_container_width=True)

# 📤 Exportar Excel
with st.sidebar:
    st.markdown("### 📥 Exportar Head Count")
    buffer = BytesIO()

    df_export = df.copy()
    df_export["setor"] = df_export["setor"].map(lambda x: setores.get(x, {}).get("label", x))
    df_export = df_export[["setor", "nome", "matricula", "funcao", "equipe"]].sort_values(by=["setor", "nome"])

    df_export.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="📄 Baixar como Excel",
        data=buffer,
        file_name="headcount_por_setor.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
