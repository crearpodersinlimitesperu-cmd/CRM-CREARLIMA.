import sys
import os
import pandas as pd

# Add directories to path
sys.path.append(r"c:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA")
sys.path.append(r"c:\Users\josem\Downloads\bot-cpsl-review")

try:
    from app_buscador import load_master, load_history, load_gestion, load_auditoria, load_respuestas
    print("Functions imported successfully!")
    df_m = load_master()
    print("load_master() shape:", df_m.shape)
    df_h = load_history()
    print("load_history() shape:", df_h.shape)
    df_g = load_gestion()
    print("load_gestion() shape:", df_g.shape)
    df_a = load_auditoria()
    print("load_auditoria() shape:", df_a.shape)
    df_r = load_respuestas()
    print("load_respuestas() shape:", df_r.shape)
except Exception as e:
    import traceback
    traceback.print_exc()
