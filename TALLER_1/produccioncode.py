# crear_gantt_desde_excel.py
import pandas as pd
import matplotlib.pyplot as plt
import os
import re

file_path = "diagrama_gantt.xlsx"  # coloca este archivo en la misma carpeta que el script

def find_header_row(path, header_candidates=("Actividad","Activ","Actividad")):
    # lee primeras 10 filas sin header para buscar la fila que contiene 'Actividad' u otro encabezado
    tmp = pd.read_excel(path, header=None, nrows=15)
    for idx, row in tmp.iterrows():
        for cell in row:
            if isinstance(cell, str) and any(h.lower() in cell.lower() for h in header_candidates):
                return idx
    return None

def choose_column(cols, keywords):
    cols_lower = {c.lower(): c for c in cols}
    for kw in keywords:
        for low, orig in cols_lower.items():
            if kw.lower() in low:
                return orig
    # fallback: try exact matches
    for kw in keywords:
        if kw in cols:
            return kw
    return None

def read_and_normalize(path):
    header_row = find_header_row(path)
    if header_row is None:
        # try usual: header = 1 (your file used that before)
        header_row = 1
    df = pd.read_excel(path, header=header_row)
    cols = list(df.columns)

    # heurística para identificar columnas
    act_col = choose_column(cols, ["actividad","operacion","operación","op"])
    start_col = choose_column(cols, ["inicio","start","tiempo inicio","start_time"])
    end_col = choose_column(cols, ["fin","finish","end","fin."])
    dur_col = choose_column(cols, ["duración","duracion","c (","c)","c ","tiempo (s)","tiempo"])
    prec_col = choose_column(cols, ["precedencia","prede","pred","antecesor"])

    mapping = {}
    if act_col: mapping[act_col] = "Actividad"
    if start_col: mapping[start_col] = "Inicio"
    if end_col: mapping[end_col] = "Fin"
    if dur_col: mapping[dur_col] = "Duracion"
    if prec_col: mapping[prec_col] = "Precedencia"

    df = df.rename(columns=mapping)

    # Keep only relevant columns if exist
    for col in ["Actividad","Inicio","Fin","Duracion","Precedencia"]:
        if col not in df.columns:
            df[col] = pd.NA

    # Convert numeric columns
    df["Inicio"] = pd.to_numeric(df["Inicio"], errors="coerce")
    df["Fin"]    = pd.to_numeric(df["Fin"], errors="coerce")
    df["Duracion"] = pd.to_numeric(df["Duracion"], errors="coerce")

    # If Duracion missing but Inicio/Fin present -> compute Duracion
    mask_dur = df["Duracion"].isna() & df["Inicio"].notna() & df["Fin"].notna()
    if mask_dur.any():
        df.loc[mask_dur, "Duracion"] = df.loc[mask_dur, "Fin"] - df.loc[mask_dur, "Inicio"]

    # If Inicio/Fin missing but Duracion + Precedencia present -> compute ES/EF (simple CPM forward)
    if df["Inicio"].isna().any() and df["Duracion"].notna().all():
        # attempt to compute ES/EF using precedence column (only if Precedencia info exists)
        if df["Precedencia"].notna().any():
            # build adjacency using Precedencia lists (comma separated)
            G = {}
            durations = {}
            for _, r in df.iterrows():
                act = r["Actividad"]
                durations[act] = float(r["Duracion"])
                preds = []
                if pd.notna(r["Precedencia"]) and str(r["Precedencia"]).strip() != "":
                    preds = [p.strip() for p in str(r["Precedencia"]).split(",") if p.strip()!=""]
                G[act] = preds
            # forward pass in topological order (simple approach)
            # compute ES
            ES = {}
            EF = {}
            # naive topo sort via repeated selection
            remaining = set(G.keys())
            while remaining:
                progressed = False
                for act in list(remaining):
                    preds = G[act]
                    if all(p in EF for p in preds):
                        es = 0 if len(preds)==0 else max(EF[p] for p in preds)
                        ES[act] = es
                        EF[act] = es + durations[act]
                        remaining.remove(act)
                        progressed = True
                if not progressed:
                    # cycle or missing preds
                    break
            # fill df
            for i, r in df.iterrows():
                act = r["Actividad"]
                if act in ES:
                    df.at[i, "Inicio"] = ES[act]
                    df.at[i, "Fin"] = EF[act]
    # final cleanup: drop rows with no actividad name
    df = df[df["Actividad"].notna()].copy()
    df.reset_index(drop=True, inplace=True)
    return df

def plot_gantt(df, out_png="gantt_diagram.png", save_excel="diagrama_gantt_grafico.xlsx"):
    # Sort by Inicio (if exists), else by order in file
    if df["Inicio"].notna().all():
        df_sorted = df.sort_values(by="Inicio", ascending=True).reset_index(drop=True)
    else:
        df_sorted = df.copy()

    # Prepare plotting
    fig, ax = plt.subplots(figsize=(12, 0.7*len(df_sorted) + 2))
    y_pos = list(range(len(df_sorted)))
    labels = df_sorted["Actividad"].astype(str).tolist()
    starts = df_sorted["Inicio"].fillna(0).astype(float).tolist()
    ends   = df_sorted["Fin"].fillna(df_sorted["Duracion"].fillna(0)).astype(float).tolist()
    widths = [e - s for s,e in zip(starts, ends)]

    ax.barh(y_pos, widths, left=starts, height=0.6, align='center', color="skyblue", edgecolor="k")
    # Annotate start->end or duration
    for i, (s,w,e) in enumerate(zip(starts,widths,ends)):
        txt = f"{int(s)} → {int(e)}" if (not pd.isna(s) and not pd.isna(e)) else (f"{int(w)}")
        # Put text centered if wide enough else put to the right
        if w >= 0.12 * max(1, max(widths or [1])):
            ax.text(s + w/2, i, txt, va='center', ha='center', fontsize=9)
        else:
            ax.text(s + w + 0.05*max(1, max(widths or [1])), i, txt, va='center', ha='left', fontsize=9)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Tiempo (s)")
    ax.set_title("Diagrama de Gantt (desde Excel)")
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    plt.tight_layout()
    # save
    fig.savefig(out_png, dpi=300)
    print(f"Gantt guardado como: {out_png}")

    # export excel with chosen columns
    out_df = df_sorted[["Actividad","Duracion","Inicio","Fin","Precedencia"]]
    out_df.to_excel(save_excel, index=False)
    print(f"Datos usados exportados a: {save_excel}")
    plt.show()

if __name__ == "__main__":
    if not os.path.exists(file_path):
        raise SystemExit(f"No se encuentra el archivo {file_path} en la carpeta actual: {os.getcwd()}")

    df = read_and_normalize(file_path)
    print("Columnas detectadas y normalizadas:")
    print(df.columns.tolist())
    print("\nVista previa de datos (primeras filas):")
    print(df.head().to_string(index=False))

    # Plot Gantt using the detected Inicio/Fin
    plot_gantt(df, out_png="gantt_diagram.png", save_excel="diagrama_gantt_grafico.xlsx")
