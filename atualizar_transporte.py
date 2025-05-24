import json
from supabase import create_client, Client
from postgrest.exceptions import APIError

SUPABASE_URL = "https://atsmhxntpvzqatifusqy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF0c21oeG50cHZ6cWF0aWZ1c3F5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzQ4MTI0MywiZXhwIjoyMDYzMDU3MjQzfQ.sd7CIY7V-q7VRQZwTpoXf0pt-MoPj7zUvYy1Rb0YW74"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Função para identificar setor com base na frota/equipe/função
def identificar_setor_id(funcao: str, equipe: str, frota: str):
    termo = f"{funcao} {equipe} {frota}".upper()
    setores = supabase.table("setores").select("id", "setor", "identificadores").execute().data

    for setor in setores:
        identificadores = setor.get("identificadores") or []
        for ident in identificadores:
            if ident.upper() in termo:
                return setor["id"]
    return None

# === Carrega os colaboradores do JSON
with open("colaboradores.json", "r", encoding="utf-8") as file:
    colaboradores = json.load(file)

for colab in colaboradores:
    try:
        nome = colab.get("Nome", "").strip().upper()
        matricula_raw = colab.get("Matrícula", "").strip() if isinstance(colab.get("Matrícula"), str) else colab.get("Matrícula")
        matricula = str(int(float(matricula_raw))) if matricula_raw else None
        funcao = colab.get("Função", "").strip().upper()
        equipe = colab.get("Equipe", "").strip().upper()
        frota = "TRANSPORTE DE MADEIRA"  # Padroniza

        if not nome or not matricula:
            print(f"❌ Dados incompletos: {nome}")
            continue

        # Apagar colaborador antigo
        supabase.table("colaboradores").delete().eq("nome", nome).execute()
        print(f"🗑️ Apagado: {nome}")

        # Identificar setor correto
        setor_id = identificar_setor_id(funcao, equipe, frota)
        if not setor_id:
            print(f"❌ Setor não identificado: {nome}")
            continue

        # Inserir colaborador novo
        supabase.table("colaboradores").insert({
            "nome": nome,
            "matricula": matricula,
            "funcao": funcao,
            "equipe": equipe,
            "frota": frota,
            "setor_id": setor_id
        }).execute()

        print(f"✅ Inserido: {nome} ({matricula})")

    except APIError as e:
        print(f"❌ Erro Supabase: {e.message}")
    except Exception as e:
        print(f"❌ Erro geral com {colab.get('Nome', '')}: {e}")
