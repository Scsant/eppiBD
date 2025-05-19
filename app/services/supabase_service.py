# app/services/supabase_service.py

from supabase import create_client
from config.settings import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime, timedelta


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def buscar_colaborador_por_matricula(matricula):
    result = supabase.table("colaboradores").select("*").eq("matricula", matricula).eq("ativo", True).execute()
    if result.data:
        return result.data[0]
    return None

# app/services/supabase_service.py

def enviar_pedido_concatenado(colaborador, lista_itens):
    tipos = ", ".join(item["tipo"] for item in lista_itens)
    descricoes = ", ".join(item["descricao"] for item in lista_itens)
    quantidades = ", ".join(str(item["quantidade"]) for item in lista_itens)
    codigos_sap = ", ".join(item.get("codigo_sap", "") for item in lista_itens)

    payload = {
        "nome": colaborador["nome"],
        "matricula": colaborador["matricula"],
        "funcao": colaborador["funcao"],
        "equipe": colaborador["equipe"],
        "frota": colaborador.get("frota", ""),
        "centro_custo": colaborador.get("centro_custo", ""),
        "tipos": tipos,
        "descricoes": descricoes,
        "quantidades": quantidades,
        "codigos_sap": codigos_sap,
        "data_solicitacao": datetime.now().isoformat(),
        "status": "PENDENTE"
    }

    supabase.table("solicitacoes_epi").insert(payload).execute()


# app/services/supabase_service.py (continue nesse arquivo)

def listar_categorias_epis():
    result = supabase.table("epis").select("categoria").execute()
    categorias = list({row["categoria"] for row in result.data if row["categoria"]})
    categorias.sort()
    return categorias

def listar_epis_por_categoria(categoria):
    result = supabase.table("epis").select("nome").eq("categoria", categoria).execute()
    return [row["nome"] for row in result.data if row["nome"]]



def colaborador_ja_solicitou_na_semana(matricula: str) -> bool:
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday() + 1)  # Domingo
    inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)

    result = supabase.table("solicitacoes_epi") \
        .select("data_solicitacao") \
        .eq("matricula", matricula) \
        .gte("data_solicitacao", inicio_semana.isoformat()) \
        .execute()

    return bool(result.data)

def listar_solicitacoes():
    result = supabase.table("solicitacoes_epi").select("*").order("data_solicitacao", desc=True).execute()
    return result.data

def excluir_por_ids(lista_ids):
    for id_ in lista_ids:
        supabase.table("solicitacoes_epi").delete().eq("id", id_).execute()

def limpar_todas_solicitacoes():
    supabase.table("solicitacoes_epi").delete().neq("id", "").execute()


def listar_colaboradores():
    result = supabase.table("colaboradores").select("*").order("nome").execute()
    return result.data

def inserir_colaborador(data: dict):
    supabase.table("colaboradores").insert(data).execute()

def atualizar_colaborador(colaborador_id: str, data: dict):
    supabase.table("colaboradores").update(data).eq("id", colaborador_id).execute()

def excluir_colaboradores(lista_ids):
    for cid in lista_ids:
        supabase.table("colaboradores").delete().eq("id", cid).execute()



