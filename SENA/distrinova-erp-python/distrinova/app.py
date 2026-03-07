"""
app.py — DistriNova ERP v2.0
Archivo principal · Ejecutar con: streamlit run app.py
"""
import streamlit as st
import pandas as pd
from database import supabase
from datetime import datetime

# ── Configuración de la página ──────────────────────────
st.set_page_config(
    page_title="DistriNova ERP",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Estilo visual personalizado ─────────────────────────
st.markdown("""
<style>
    /* Fondo y tipografía general */
    .stApp { background-color: #0B1929; color: #E8F0F8; }
    .stSidebar { background-color: #0F2235 !important; }

    /* Métricas */
    [data-testid="metric-container"] {
        background: #152D44;
        border: 1px solid rgba(30,136,229,.2);
        border-radius: 12px;
        padding: 16px;
    }
    [data-testid="stMetricLabel"] { color: #8BA8C4 !important; font-size: 12px; }
    [data-testid="stMetricValue"] { color: #42A5F5 !important; font-size: 28px; font-weight: 800; }

    /* Tablas */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #1565C0, #1E88E5);
        color: white; border: none; border-radius: 8px;
        font-weight: 700; padding: 8px 20px;
    }
    .stButton > button:hover { opacity: 0.85; }

    /* Inputs */
    .stSelectbox > div, .stNumberInput > div, .stTextInput > div {
        background: #1A3550 !important;
    }

    /* Título principal */
    h1 { color: #42A5F5 !important; font-size: 28px !important; }
    h2 { color: #E8F0F8 !important; }
    h3 { color: #8BA8C4 !important; font-size: 14px !important; }

    /* Sidebar nav */
    .stRadio > label { color: #8BA8C4; font-size: 14px; }
    .css-1d391kg { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Constantes del negocio ───────────────────────────────
RUTAS = {
    "Santa Rosa de Osos": {"km": 77.4,  "tiempo": "1h 20min", "salida_max": "03:40"},
    "Yarumal":            {"km": 122.4, "tiempo": "2h 10min", "salida_max": "02:50"},
    "Valdivia":           {"km": 174,   "tiempo": "3h 00min", "salida_max": "02:00"},
    "Taraza":             {"km": 249,   "tiempo": "4h 10min", "salida_max": "00:50"},
    "Caucasia":           {"km": 283,   "tiempo": "4h 45min", "salida_max": "00:15"},
}
CEDIS = ["Medellín", "Santa Rosa", "Taraza"]
CAP_FURGONETA = 168  # tortas máximo por vehículo
TARIFA_KM = 3000     # pesos colombianos por km


# ════════════════════════════════════════
# FUNCIONES DE BASE DE DATOS
# ════════════════════════════════════════

def get_inventario():
    """Obtiene el stock actual de todos los CEDI."""
    try:
        db = supabase()
        res = db.table("inventario").select("*").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar inventario: {e}")
        return pd.DataFrame()

def get_despachos():
    """Obtiene todos los despachos registrados."""
    try:
        db = supabase()
        res = db.table("despachos").select("*").order("created_at", desc=True).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar despachos: {e}")
        return pd.DataFrame()

def get_pedidos():
    """Obtiene todos los pedidos."""
    try:
        db = supabase()
        res = db.table("pedidos").select("*").order("created_at", desc=True).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def get_movimientos():
    """Obtiene la bitácora de movimientos de inventario."""
    try:
        db = supabase()
        res = db.table("movimientos").select("*").order("created_at", desc=True).limit(100).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()


# ════════════════════════════════════════
# SIDEBAR — NAVEGACIÓN
# ════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🚚 DistriNova ERP")
    st.markdown("*siempre a tiempo, siempre en ruta*")
    st.markdown("---")

    pagina = st.radio(
        "Navegar",
        options=[
            "📊 Dashboard",
            "🗺️ Planeador de Rutas",
            "💵 Cotizador TMS",
            "📦 Inventario CEDI",
            "🛒 Pedidos",
            "📋 Historial",
            "📄 Documentos",
            "👥 Equipo",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown(f"🕐 **{datetime.now().strftime('%H:%M:%S')}**")
    st.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown("---")

    # Usuario activo
    usuario = st.selectbox(
        "👤 Usuario activo",
        ["Yoany (COO)", "Gómez (Logística)", "Karen (Inventarios)", "Laura (Aux.)", "Mafe (Docs)"],
        label_visibility="visible"
    )


# ════════════════════════════════════════
# PÁGINA: DASHBOARD
# ════════════════════════════════════════
if pagina == "📊 Dashboard":
    st.title("📊 Panel de Control DistriNova")
    st.caption("Operación en tiempo real · Norte de Antioquia")

    # Cargar datos
    inv_df    = get_inventario()
    desp_df   = get_despachos()
    pedidos_df = get_pedidos()

    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)

    stock_total = inv_df["stock"].sum() if not inv_df.empty else 0
    total_viajes = len(desp_df)
    total_fletes = desp_df["costo_flete"].sum() if not desp_df.empty else 0
    total_tortas = desp_df["tortas"].sum() if not desp_df.empty else 0

    with col1:
        st.metric("📦 Stock Total", f"{stock_total:,}", help="Suma de tortas en los 3 CEDI")
    with col2:
        st.metric("🚐 Viajes Registrados", total_viajes, help="Despachos de la semana")
    with col3:
        st.metric("💰 Costo Fletes", f"${total_fletes:,.0f}", help="Acumulado de fletes")
    with col4:
        st.metric("🎂 Tortas Despachadas", f"{total_tortas:,}", help="Total unidades entregadas")

    st.markdown("---")

    # Segunda fila KPIs
    col5, col6, col7, col8 = st.columns(4)
    alertas = 0
    if not inv_df.empty:
        alertas = len(inv_df[inv_df["stock"] <= inv_df["stock_min"]])
    cpt = int(total_fletes / total_tortas) if total_tortas > 0 else 0
    furgs_500 = -(-500 // CAP_FURGONETA)  # ceil division
    furgs_600 = -(-600 // CAP_FURGONETA)

    with col5:
        st.metric("⚠️ Alertas Stock", alertas, delta="CEDI bajo mínimo", delta_color="inverse")
    with col6:
        st.metric("💵 Costo / Torta", f"${cpt:,}" if cpt else "—", help="Solo flete")
    with col7:
        st.metric("🚐 Furgonetas 500 tortas", furgs_500)
    with col8:
        st.metric("🚐 Furgonetas 600 tortas (pico)", furgs_600)

    st.markdown("---")

    # Alertas visuales de stock
    if not inv_df.empty:
        for _, row in inv_df.iterrows():
            if row["stock"] <= row["stock_min"]:
                st.error(f"🚨 **RUPTURA INMINENTE — CEDI {row['cedi']}:** Solo {row['stock']} tortas. Mínimo: {row['stock_min']}. ¡Emitir orden de compra!")
            elif row["stock"] <= row["stock_min"] * 2:
                st.warning(f"⚠️ **Stock bajo — CEDI {row['cedi']}:** {row['stock']} tortas disponibles.")

    # Inventario visual
    st.subheader("🏭 Inventario por CEDI")
    if not inv_df.empty:
        cols = st.columns(len(inv_df))
        for i, (_, row) in enumerate(inv_df.iterrows()):
            with cols[i]:
                pct = min(100, int(row["stock"] / max(row["stock_min"] * 4, 1) * 100))
                color = "🟢" if row["stock"] > row["stock_min"] * 2 else "🟡" if row["stock"] > row["stock_min"] else "🔴"
                st.metric(
                    f"{color} CEDI {row['cedi']}",
                    f"{row['stock']} tortas",
                    help=f"Mínimo: {row['stock_min']}"
                )
                st.progress(pct / 100)

    # Últimos despachos
    st.subheader("🚐 Últimos Despachos")
    if not desp_df.empty:
        cols_show = ["remision", "cedi_origen", "destino", "tortas", "furgonetas", "costo_flete", "nocturno", "created_at"]
        cols_exist = [c for c in cols_show if c in desp_df.columns]
        st.dataframe(
            desp_df[cols_exist].head(10).rename(columns={
                "remision": "Remisión", "cedi_origen": "Origen",
                "destino": "Destino", "tortas": "Tortas",
                "furgonetas": "Furgonetas", "costo_flete": "Flete ($)",
                "nocturno": "Nocturno", "created_at": "Fecha"
            }),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Sin despachos registrados aún.")

    if st.button("🔄 Actualizar datos"):
        st.rerun()


# ════════════════════════════════════════
# PÁGINA: PLANEADOR DE RUTAS
# ════════════════════════════════════════
elif pagina == "🗺️ Planeador de Rutas":
    st.title("🗺️ Planeador de Rutas")
    st.info("⏰ **Restricción:** Todas las entregas deben llegar **antes de las 5:00 A.M.** Las furgonetas salen desde Medellín.")

    col_form, col_result = st.columns([1, 1])

    with col_form:
        st.subheader("⚙️ Configurar Despacho")

        municipio = st.selectbox("Municipio de entrega", list(RUTAS.keys()))
        cantidad  = st.number_input("Cantidad de tortas", min_value=1, max_value=1000, value=168, step=1)
        hora_sal  = st.time_input("Hora de salida desde Medellín", value=None)
        nocturno  = st.checkbox("🌙 Jornada Nocturna (+30%)", value=True)
        ida_vuelta = st.checkbox("🔄 Incluir regreso vacío (doble km)", value=True)

        registrar = st.button("🚐 Registrar este Despacho", use_container_width=True)

    # Cálculos
    r = RUTAS[municipio]
    km_total = r["km"] * 2 if ida_vuelta else r["km"]
    furgonetas = -(-cantidad // CAP_FURGONETA)  # ceiling
    costo_base = km_total * TARIFA_KM * furgonetas
    costo_final = int(costo_base * 1.3 if nocturno else costo_base)
    cpt = int(costo_final / cantidad)

    with col_result:
        st.subheader("📋 Propuesta de Trazabilidad")

        # Verificar horario
        [sh, sm] = r["salida_max"].split(":")
        hora_ok = True
        if hora_sal:
            hora_ok = (hora_sal.hour < int(sh)) or (hora_sal.hour == int(sh) and hora_sal.minute <= int(sm))
            if hora_ok:
                st.success(f"✅ Horario factible. Llegas antes de las 5:00 AM.")
            else:
                st.error(f"⛔ Con salida a las {hora_sal} no llegas a tiempo. Salida máxima: {r['salida_max']} AM.")

        # Verificar stock
        inv_df = get_inventario()
        stock_mde = inv_df.loc[inv_df["cedi"] == "Medellín", "stock"].values
        stock_actual = int(stock_mde[0]) if len(stock_mde) > 0 else 0
        if stock_actual < cantidad:
            st.error(f"🚨 Stock insuficiente. CEDI Medellín: {stock_actual} tortas disponibles.")

        # Tabla de resultados
        data_result = {
            "Campo": ["🗺️ Ruta", "📏 Distancia", "⏱️ Tiempo estimado",
                      "🚦 Salida máxima recomendada", "🚐 Furgonetas necesarias",
                      "🎂 Tortas", "💵 Tipo de jornada", "💵 Costo flete",
                      "💰 Costo por torta (flete)"],
            "Valor": [f"Medellín → {municipio}", f"{km_total:.1f} km", r["tiempo"],
                      f"{r['salida_max']} AM", f"{furgonetas} furgoneta{'s' if furgonetas > 1 else ''}",
                      str(cantidad), "🌙 Nocturna" if nocturno else "☀️ Diurna",
                      f"${costo_final:,}", f"${cpt:,}"]
        }
        st.dataframe(pd.DataFrame(data_result), use_container_width=True, hide_index=True)

        st.metric("💵 TOTAL FLETE", f"${costo_final:,}")

    # Registrar despacho en BD
    if registrar:
        if stock_actual < cantidad:
            st.error("No se puede registrar: stock insuficiente.")
        else:
            db = supabase()
            # Descontar inventario
            db.table("inventario").update({
                "stock": stock_actual - cantidad,
                "updated_at": datetime.now().isoformat()
            }).eq("cedi", "Medellín").execute()

            # Número de remisión
            desp_count = len(get_despachos())
            num_rem = f"REM-{1001 + desp_count}"

            # Registrar despacho
            db.table("despachos").insert({
                "remision": num_rem,
                "cedi_origen": "Medellín",
                "destino": municipio,
                "km": km_total,
                "tortas": cantidad,
                "furgonetas": furgonetas,
                "nocturno": nocturno,
                "costo_flete": costo_final,
                "usuario": usuario.split(" ")[0]
            }).execute()

            # Registrar movimiento
            db.table("movimientos").insert({
                "cedi": "Medellín",
                "tipo": "salida",
                "cantidad": cantidad,
                "documento": num_rem,
                "stock_result": stock_actual - cantidad,
                "usuario": usuario.split(" ")[0]
            }).execute()

            st.success(f"✅ Despacho **{num_rem}** registrado. {cantidad} tortas → {municipio}. Flete: **${costo_final:,}**")
            st.balloons()

    # Tabla maestra de rutas
    st.markdown("---")
    st.subheader("📊 Tabla Maestra de Rutas")
    tabla_rutas = []
    for mun, dat in RUTAS.items():
        c_diurno  = int(dat["km"] * TARIFA_KM)
        c_nocturno = int(c_diurno * 1.3)
        tabla_rutas.append({
            "Municipio": mun, "KM": dat["km"],
            "Tiempo": dat["tiempo"],
            "Flete 1 Furg. (diurno)": f"${c_diurno:,}",
            "Flete 1 Furg. (nocturno)": f"${c_nocturno:,}",
            "Salida máx. (5AM)": dat["salida_max"],
        })
    st.dataframe(pd.DataFrame(tabla_rutas), use_container_width=True, hide_index=True)


# ════════════════════════════════════════
# PÁGINA: COTIZADOR TMS
# ════════════════════════════════════════
elif pagina == "💵 Cotizador TMS":
    st.title("💵 Cotizador TMS Automático")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚙️ Parámetros")
        ruta_cot   = st.selectbox("Ruta", list(RUTAS.keys()), key="cot_ruta")
        qty_cot    = st.number_input("Cantidad de tortas", min_value=1, value=168, key="cot_qty")
        pvp_cot    = st.number_input("Precio de venta / torta ($)", min_value=0, value=25000, key="cot_pvp")
        noc_cot    = st.checkbox("🌙 Jornada Nocturna (+30%)", key="cot_noc")
        ida_cot    = st.checkbox("🔄 Incluir regreso vacío", value=True, key="cot_ida")
        aux_cot    = st.number_input("Aux. cargue/descargue ($)", value=50000, key="cot_aux")
        otros_cot  = st.number_input("Otros costos operativos ($)", value=30000, key="cot_otros")
        costo_prod = st.number_input("Costo producción / torta ($)", value=12000, key="cot_prod")

    with col2:
        st.subheader("📊 Resultado")
        rc = RUTAS[ruta_cot]
        km_c = rc["km"] * 2 if ida_cot else rc["km"]
        furgs_c = -(-qty_cot // CAP_FURGONETA)
        flete_base = km_c * TARIFA_KM * furgs_c
        flete_final = int(flete_base * 1.3 if noc_cot else flete_base)
        costo_total_op = flete_final + aux_cot + otros_cot
        costo_total_torta = costo_prod + int(costo_total_op / qty_cot)
        ingreso = qty_cot * pvp_cot
        margen_pesos = ingreso - (qty_cot * costo_total_torta)
        margen_pct = int((margen_pesos / ingreso) * 100) if ingreso > 0 else 0

        st.metric("🚐 Furgonetas necesarias", furgs_c)
        st.metric("💵 Costo flete total", f"${flete_final:,}")
        st.metric("💰 Costo total operación", f"${costo_total_op:,}")
        st.metric("🎂 Costo total / torta", f"${costo_total_torta:,}")

        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("💵 Ingreso bruto", f"${ingreso:,}")
        with col_b:
            delta_color = "normal" if margen_pct > 20 else "inverse"
            st.metric("📈 Margen", f"{margen_pct}%",
                      delta=f"${margen_pesos:,}", delta_color=delta_color)

        if margen_pct >= 25:
            st.success(f"✅ Margen saludable ({margen_pct}%). Precio de venta adecuado.")
        elif margen_pct >= 10:
            st.warning(f"⚠️ Margen bajo ({margen_pct}%). Considera subir el precio.")
        else:
            st.error(f"❌ Margen negativo o muy bajo ({margen_pct}%). Revisa los costos.")

        st.info(f"💡 **Precio mínimo sugerido** para 30% de margen: **${int(costo_total_torta / 0.70):,}** / torta")


# ════════════════════════════════════════
# PÁGINA: INVENTARIO
# ════════════════════════════════════════
elif pagina == "📦 Inventario CEDI":
    st.title("📦 Inventario CEDI — WMS")
    st.caption(f"Responsable: Karen · Usuario activo: {usuario}")

    inv_df = get_inventario()

    # Tarjetas de CEDI
    if not inv_df.empty:
        cols = st.columns(len(inv_df))
        for i, (_, row) in enumerate(inv_df.iterrows()):
            with cols[i]:
                pct = min(1.0, row["stock"] / max(row["stock_min"] * 4, 1))
                est = "🔴 Crítico" if row["stock"] <= row["stock_min"] else \
                      "🟡 Bajo" if row["stock"] <= row["stock_min"] * 2 else "🟢 Normal"
                st.metric(f"CEDI {row['cedi']}", f"{row['stock']} tortas", est)
                st.progress(pct)
                st.caption(f"Mínimo: {row['stock_min']}")

    st.markdown("---")
    col_form, col_bita = st.columns([1, 1])

    with col_form:
        st.subheader("➕ Registrar Movimiento")
        cedi_sel  = st.selectbox("CEDI", CEDIS, key="inv_cedi")
        tipo_sel  = st.selectbox("Tipo", ["entrada", "salida", "ajuste"], key="inv_tipo")
        qty_inv   = st.number_input("Cantidad de tortas", min_value=1, key="inv_qty")
        doc_inv   = st.text_input("Documento soporte", placeholder="Ej: OC-2026-001", key="inv_doc")

        if st.button("📥 Registrar Movimiento", use_container_width=True):
            db = supabase()
            stock_row = inv_df[inv_df["cedi"] == cedi_sel]
            stock_act = int(stock_row["stock"].values[0]) if not stock_row.empty else 0

            if tipo_sel == "salida" and stock_act < qty_inv:
                st.error(f"❌ Stock insuficiente. Disponible: {stock_act} tortas.")
            else:
                nuevo = stock_act + qty_inv if tipo_sel == "entrada" else \
                        stock_act - qty_inv if tipo_sel == "salida" else int(qty_inv)

                db.table("inventario").update({
                    "stock": nuevo, "updated_at": datetime.now().isoformat()
                }).eq("cedi", cedi_sel).execute()

                db.table("movimientos").insert({
                    "cedi": cedi_sel, "tipo": tipo_sel,
                    "cantidad": qty_inv, "documento": doc_inv or "Sin doc",
                    "stock_result": nuevo, "usuario": usuario.split(" ")[0]
                }).execute()

                st.success(f"✅ {cedi_sel}: {stock_act} → **{nuevo}** tortas.")
                st.rerun()

    with col_bita:
        st.subheader("📋 Bitácora de Movimientos")
        mov_df = get_movimientos()
        if not mov_df.empty:
            cols_show = [c for c in ["created_at", "cedi", "tipo", "cantidad", "documento", "stock_result"] if c in mov_df.columns]
            st.dataframe(
                mov_df[cols_show].rename(columns={
                    "created_at": "Fecha", "cedi": "CEDI",
                    "tipo": "Tipo", "cantidad": "Cantidad",
                    "documento": "Documento", "stock_result": "Stock Resultado"
                }),
                use_container_width=True, hide_index=True, height=350
            )
        else:
            st.info("Sin movimientos registrados.")


# ════════════════════════════════════════
# PÁGINA: PEDIDOS
# ════════════════════════════════════════
elif pagina == "🛒 Pedidos":
    st.title("🛒 Gestión de Pedidos")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Nuevo Pedido")
        actor_ped  = st.selectbox("Actor", ["Mayorista → DistriNova", "Minorista → DistriNova",
                                             "DistriNova → Fabricante", "Min. Defensa → DistriNova"])
        dest_ped   = st.selectbox("Municipio destino", list(RUTAS.keys()))
        qty_ped    = st.number_input("Cantidad de tortas", min_value=1, value=168)
        pvp_ped    = st.number_input("Precio unitario ($)", min_value=0, value=25000)
        obs_ped    = st.text_area("Observaciones", height=80, placeholder="Instrucciones especiales...")

        if st.button("🛒 Crear Pedido", use_container_width=True):
            db = supabase()
            total_ped = qty_ped * pvp_ped
            db.table("pedidos").insert({
                "actor": actor_ped, "destino": dest_ped,
                "cantidad": qty_ped, "precio_unit": pvp_ped,
                "total": total_ped, "observaciones": obs_ped,
                "usuario": usuario.split(" ")[0]
            }).execute()
            st.success(f"✅ Pedido creado. {qty_ped} tortas → {dest_ped}. Total: **${total_ped:,}**")
            st.rerun()

    with col2:
        st.subheader("📊 Pedidos Registrados")
        ped_df = get_pedidos()
        if not ped_df.empty:
            st.metric("Total pedidos", len(ped_df))
            st.metric("Total tortas", f"{ped_df['cantidad'].sum():,}")
            st.metric("Valor total", f"${ped_df['total'].sum():,}")
        st.dataframe(ped_df if not ped_df.empty else pd.DataFrame(), use_container_width=True, hide_index=True)


# ════════════════════════════════════════
# PÁGINA: HISTORIAL
# ════════════════════════════════════════
elif pagina == "📋 Historial":
    st.title("📋 Historial de Transacciones")

    desp_df = get_despachos()
    ped_df  = get_pedidos()
    mov_df  = get_movimientos()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("🚐 Despachos", len(desp_df))
    with col2: st.metric("🛒 Pedidos", len(ped_df))
    with col3: st.metric("🎂 Tortas despachadas", f"{desp_df['tortas'].sum():,}" if not desp_df.empty else 0)
    with col4: st.metric("📦 Movimientos inventario", len(mov_df))

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🚐 Despachos", "🛒 Pedidos", "📦 Movimientos"])

    with tab1:
        if not desp_df.empty:
            st.dataframe(desp_df, use_container_width=True, hide_index=True)
        else:
            st.info("Sin despachos.")

    with tab2:
        if not ped_df.empty:
            st.dataframe(ped_df, use_container_width=True, hide_index=True)
        else:
            st.info("Sin pedidos.")

    with tab3:
        if not mov_df.empty:
            st.dataframe(mov_df, use_container_width=True, hide_index=True)
        else:
            st.info("Sin movimientos.")


# ════════════════════════════════════════
# PÁGINA: DOCUMENTOS
# ════════════════════════════════════════
elif pagina == "📄 Documentos":
    st.title("📄 Remisiones y Facturas")
    st.caption(f"Responsable: Mafe · Usuario: {usuario}")

    tab_rem, tab_fac = st.tabs(["📄 Generar Remisión", "🧾 Generar Factura"])

    with tab_rem:
        desp_df = get_despachos()
        if not desp_df.empty:
            rem_sel = st.selectbox("Seleccionar despacho", desp_df["remision"].tolist())
            desp_row = desp_df[desp_df["remision"] == rem_sel].iloc[0]

            st.markdown("---")
            col_doc, _ = st.columns([2, 1])
            with col_doc:
                st.markdown(f"""
### 📄 Remisión de Despacho — {rem_sel}
---
| Campo | Valor |
|-------|-------|
| **Empresa** | DistriNova |
| **NIT** | 900.XXX.XXX-X |
| **Número** | {rem_sel} |
| **Fecha** | {desp_row.get('created_at', '')[:10]} |
| **CEDI Origen** | {desp_row['cedi_origen']} |
| **Destino** | {desp_row['destino']} |
| **Distancia** | {desp_row['km']} km |
| **Producto** | Tortas caseras (30×30×15 cm) |
| **Cantidad** | **{desp_row['tortas']} unidades** |
| **Furgonetas** | {desp_row['furgonetas']} |
| **Jornada** | {'🌙 Nocturna (+30%)' if desp_row['nocturno'] else '☀️ Diurna'} |
| **Costo flete** | **${int(desp_row['costo_flete']):,}** |
                """)
        else:
            st.info("No hay despachos registrados aún. Regístralos desde el Planeador de Rutas.")

    with tab_fac:
        st.subheader("🧾 Nueva Factura")
        col_a, col_b = st.columns(2)
        with col_a:
            cli_fac  = st.text_input("Cliente", placeholder="Nombre o empresa")
            nit_fac  = st.text_input("NIT / CC", placeholder="900.XXX.XXX-X")
            qty_fac  = st.number_input("Tortas", min_value=0, value=168)
            pvp_fac  = st.number_input("Precio unitario ($)", min_value=0, value=25000)
        with col_b:
            fle_fac  = st.number_input("Costo flete ($)", min_value=0, value=0)
            ruta_fac = st.text_input("Ruta", placeholder="Medellín → Caucasia")

        subtotal = qty_fac * pvp_fac + fle_fac
        iva      = int(subtotal * 0.19)
        total    = subtotal + iva

        st.markdown("---")
        col_x, col_y, col_z = st.columns(3)
        with col_x: st.metric("Subtotal", f"${subtotal:,}")
        with col_y: st.metric("IVA 19%", f"${iva:,}")
        with col_z: st.metric("**TOTAL**", f"${total:,}")

        if st.button("🧾 Guardar Factura", use_container_width=True):
            if not cli_fac:
                st.warning("Escribe el nombre del cliente.")
            else:
                db = supabase()
                fac_count = db.table("facturas").select("id", count="exact").execute()
                num_fac = f"FAC-{2001 + (fac_count.count or 0)}"
                db.table("facturas").insert({
                    "numero": num_fac, "cliente": cli_fac, "nit": nit_fac,
                    "cantidad": qty_fac, "precio_unit": pvp_fac,
                    "costo_flete": fle_fac, "subtotal": subtotal,
                    "iva": iva, "total": total, "ruta": ruta_fac,
                    "usuario": "Mafe"
                }).execute()
                st.success(f"✅ Factura **{num_fac}** guardada. Total: **${total:,}**")


# ════════════════════════════════════════
# PÁGINA: EQUIPO
# ════════════════════════════════════════
elif pagina == "👥 Equipo":
    st.title("👥 Equipo Directivo DistriNova")
    st.caption("*siempre a tiempo, siempre en ruta*")

    equipo = [
        {"emoji": "👑", "cargo": "Director de Operaciones (COO)", "nombre": "Yoany",  "color": "🔵", "resp": "KPIs · Junta Directiva · Estrategia"},
        {"emoji": "🗺️", "cargo": "Coordinador Logística y Tráfico", "nombre": "Gómez",  "color": "🟠", "resp": "Rutas · Recargos nocturnos · GPS"},
        {"emoji": "📦", "cargo": "Analista de Inventarios (CDI)",   "nombre": "Karen",  "color": "🟢", "resp": "Stock · Rotación · Reabastecimiento"},
        {"emoji": "🚛", "cargo": "Auxiliar de Operaciones",         "nombre": "Laura",  "color": "🟡", "resp": "Cargue · Estiba · Verificación"},
        {"emoji": "🧾", "cargo": "Facturación y Documentación",     "nombre": "Mafe",   "color": "🟠", "resp": "Facturas · Remisiones · Legalización"},
    ]

    cols = st.columns(3)
    for i, p in enumerate(equipo):
        with cols[i % 3]:
            st.markdown(f"""
**{p['emoji']} {p['nombre']}**
{p['cargo']}
*{p['resp']}*
            """)
            st.markdown("---")

    st.subheader("🏢 Identidad Corporativa")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Misión**")
        st.write("Distribuir productos alimenticios de forma eficiente y segura, asegurando disponibilidad constante y entregas confiables.")
    with col2:
        st.markdown("**Visión**")
        st.write("Ser los operadores logísticos líderes en distribución nacional, reconocidos por puntualidad, calidad y optimización de costos.")
    with col3:
        st.markdown("**Valores**")
        st.write("Puntualidad · Seguridad alimentaria · Trazabilidad · Eficiencia · Buen servicio al cliente")
