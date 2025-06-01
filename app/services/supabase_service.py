# app/services/supabase_service.py

from supabase import create_client
from config.settings import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime, timedelta


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def buscar_colaborador_por_matricula(matricula_raw):
    try:
        matricula = str(int(float(matricula_raw))).strip()
    except:
        return None

    result = supabase.table("colaboradores") \
        .select("*") \
        .eq("matricula", matricula) \
        .eq("ativo", True) \
        .execute()

    if result.data:
        return result.data[0]
    return None



def enviar_pedido_concatenado(colaborador, itens):
    from datetime import datetime

    tipos = [item.get("tipo") for item in itens if item.get("tipo")]
    descricoes = [item.get("descricao") for item in itens if item.get("descricao")]
    quantidades = [str(item.get("quantidade", 1)) for item in itens]
    codigos_sap = [str(item.get("codigo_sap")) for item in itens if item.get("codigo_sap")]

    payload = {
        "colaborador_id": colaborador["id"],
        "tipos": ", ".join(tipos),
        "descricoes": ", ".join(descricoes),
        "quantidades": ", ".join(quantidades),
        "codigos_sap": ", ".join(codigos_sap),
        "status": "pendente",
        "data_solicitacao": datetime.now().isoformat()
    }

    response = supabase.table("solicitacoes_epi").insert(payload).execute()
    print("✅ Pedido enviado:", response.data)


# app/services/supabase_service.py (continue nesse arquivo)

def listar_categorias_epis():
    result = supabase.table("epis").select("categoria").execute()
    categorias = list({row["categoria"] for row in result.data if row["categoria"]})
    categorias.sort()
    return categorias

def listar_epis_por_categoria(categoria):
    result = supabase.table("epis").select("nome").eq("categoria", categoria).execute()
    return [row["nome"] for row in result.data if row["nome"]]





def colaborador_ja_solicitou_na_semana(colaborador_id: str) -> bool:
    hoje = datetime.now()

    # Define o início da semana (domingo às 00:00)
    inicio_semana = hoje - timedelta(days=hoje.weekday() + 1)
    inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)

    result = supabase.table("solicitacoes_epi") \
        .select("id") \
        .eq("colaborador_id", colaborador_id) \
        .gte("data_solicitacao", inicio_semana.isoformat()) \
        .execute()

    return bool(result.data)

def listar_solicitacoes():
    result = supabase.table("vw_solicitacoes_analista") \
        .select("id, nome, matricula, funcao, equipe, frota, centro_custo, tipos, descricoes, quantidades, codigos_sap, status, data_solicitacao") \
        .order("data_solicitacao", desc=True) \
        .execute()
    return result.data


def excluir_por_ids(lista_ids):
    for id_ in lista_ids:
        supabase.table("solicitacoes_epi").delete().eq("id", id_).execute()

def limpar_todas_solicitacoes():
    supabase.table("solicitacoes_epi").delete().neq("id", "").execute()


def listar_colaboradores():
    todos = []
    batch_size = 1000
    offset = 0

    while True:
        response = supabase.table("colaboradores") \
            .select("*") \
            .order("nome") \
            .range(offset, offset + batch_size - 1) \
            .execute()

        data = response.data or []
        todos.extend(data)

        if len(data) < batch_size:
            break

        offset += batch_size

    return todos


def inserir_colaborador(data: dict):
    supabase.table("colaboradores").insert(data).execute()

def atualizar_colaborador(colaborador_id: str, data: dict):
    supabase.table("colaboradores").update(data).eq("id", colaborador_id).execute()

def excluir_colaboradores(lista_ids):
    for cid in lista_ids:
        supabase.table("colaboradores").delete().eq("id", cid).execute()



def listar_totais_por_setor():
    response = supabase.table("vw_colaboradores_com_setor").select("*").execute()
    return response.data

def listar_colaboradores_com_setor():
    todos = []
    batch_size = 1000
    offset = 0

    while True:
        response = supabase.table("vw_colaboradores_com_setor") \
            .select("*") \
            .order("nome") \
            .range(offset, offset + batch_size - 1) \
            .execute()

        data = response.data or []
        todos.extend(data)

        if len(data) < batch_size:
            break

        offset += batch_size

    return todos



def buscar_quantidade_permitida(epi_nome):
    result = supabase.table("epis") \
        .select("quantidade_permitida") \
        .eq("nome", epi_nome) \
        .single() \
        .execute()

    if result.data:
        return int(result.data["quantidade_permitida"])
    return None
def listar_requisicoes_sap_agrupadas():
    result = supabase.table("vw_requisicoes_sap_agrupadas_final") \
        .select("*") \
        .execute()
    return result.data

def listar_colaboradores_com_detalhes():
    todos = []
    batch_size = 1000
    offset = 0

    while True:
        response = supabase.table("vw_solicitacoes_detalhadas") \
            .select("*") \
            .range(offset, offset + batch_size - 1) \
            .order("nome") \
            .execute()

        data = response.data or []
        todos.extend(data)

        if len(data) < batch_size:
            break

        offset += batch_size

    return todos
