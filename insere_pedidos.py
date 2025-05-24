import json
from datetime import datetime
from supabase import create_client, Client

SUPABASE_URL = "https://atsmhxntpvzqatifusqy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF0c21oeG50cHZ6cWF0aWZ1c3F5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzQ4MTI0MywiZXhwIjoyMDYzMDU3MjQzfQ.sd7CIY7V-q7VRQZwTpoXf0pt-MoPj7zUvYy1Rb0YW74"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Abre o JSON ===
with open("pedidos_completos.json", "r", encoding="utf-8") as file:
    pedidos = json.load(file)

def buscar_colaborador_id(matricula: str):
    try:
        mat = str(int(float(matricula.strip())))
    except:
        return None
    response = supabase.table("colaboradores").select("id").eq("matricula", mat).eq("ativo", True).execute()
    if response.data:
        return response.data[0]["id"]
    return None

# === Processa e envia ===
for pedido in pedidos:
    matricula = pedido.get("Matrícula")
    colaborador_id = buscar_colaborador_id(matricula)

    if not colaborador_id:
        print(f"❌ Colaborador não encontrado: {matricula}")
        continue

    tipo = pedido.get("Tipo", "").strip()
    descricao = pedido.get("Descrição", "").strip()
    quantidade = pedido.get("Quantidade", "").strip()

    payload = {
        "colaborador_id": colaborador_id,
        "tipos": tipo,
        "descricoes": descricao,
        "quantidades": quantidade,
        "status": "pendente",
        "data_solicitacao": datetime.now().isoformat()
    }

    try:
        response = supabase.table("solicitacoes_epi").insert(payload).execute()
        print(f"✅ Pedido inserido para matrícula {matricula}")
    except Exception as e:
        print(f"❌ Erro ao inserir pedido de {matricula}: {e}")
