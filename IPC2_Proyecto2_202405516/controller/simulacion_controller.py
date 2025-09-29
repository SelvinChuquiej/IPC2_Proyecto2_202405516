from flask import Blueprint, request, redirect, url_for, flash, current_app, render_template
from models.ListaEnlazada import ListaEnlazada

simulacion_bp = Blueprint('simulacion', __name__)

# Exclusivamente para mostrar los datos en el template.
def lista_enlazada_a_lista(le):
    valores = []
    nodo = le.primero
    while nodo:
        valores.append(nodo.dato)
        nodo = nodo.siguiente
    return valores

def _get_at(lista, idx):
    n = lista.primero
    i = 0
    while n is not None and i < idx:
        n = n.siguiente
        i += 1
    return n

def _set_at(lista, idx, value):
    n = _get_at(lista, idx)
    if n is not None:
        n.dato = value

def _append_fila(tabla_acciones, segundo, *acciones):
    fila = f"<tr><td>{segundo} segundo</td>"
    for acc in acciones:
        fila += f"<td>{acc}</td>"
    fila += "</tr>\n"
    return tabla_acciones + fila

# --- Búsquedas y reglas de negocio ---
def _buscar_instruccion_dron(instrucciones_pendientes, instrucciones_completadas, dron_idx):
    nodo_inst = instrucciones_pendientes.primero
    nodo_comp = instrucciones_completadas.primero
    while nodo_inst:
        partes = nodo_inst.dato.split('-')
        h = int(partes[0][1:])
        p = int(partes[1][1:])
        if h == dron_idx + 1 and nodo_comp.dato == 0:
            return (nodo_inst, p)
        nodo_inst = nodo_inst.siguiente
        nodo_comp = nodo_comp.siguiente
    return None

def _tiene_instrucciones_pendientes(instrucciones_pendientes, instrucciones_completadas, dron_idx):
    nodo_inst = instrucciones_pendientes.primero
    nodo_comp = instrucciones_completadas.primero
    while nodo_inst:
        partes = nodo_inst.dato.split('-')
        h = int(partes[0][1:])
        if nodo_comp.dato == 0 and h == dron_idx + 1:
            return True
        nodo_inst = nodo_inst.siguiente
        nodo_comp = nodo_comp.siguiente
    return False

def _actualizar_accion_dron(dron_idx, acciones, nueva_accion):
    n = _get_at(acciones, dron_idx)
    if n is not None:
        n.dato = nueva_accion

def _puede_regar(dron_idx, planta_objetivo, dron_pos, dron_movido):
    pos = _get_at(dron_pos, dron_idx).dato
    movio = _get_at(dron_movido, dron_idx).dato
    return (pos == planta_objetivo) and (not movio)

def buscar_planta(invernadero, hilera_num, planta_num):
    for hilera in invernadero.hileras:
        if hilera.numero == hilera_num:
            for planta in hilera.plantas:
                if planta.posicion == planta_num:
                    return planta
    return None

# --- Simulación principal ---
def calcular_consumos(plan, invernadero):
    tiempo_total = 0
    agua_total = 0
    fertilizante_total = 0

    num_hileras = invernadero.num_hileras
    agua_por_dron = ListaEnlazada()
    fertilizante_por_dron = ListaEnlazada()
    for _ in range(num_hileras):
        agua_por_dron.insertar(0)
        fertilizante_por_dron.insertar(0)

    instrucciones_pendientes = ListaEnlazada()
    for pedazo in plan.instrucciones_original.split(", "):
        inst = pedazo.strip()
        if plan.validar_formato(inst):
            instrucciones_pendientes.insertar(inst)

    dron_pos = ListaEnlazada()
    dron_fin = ListaEnlazada()
    instrucciones_completadas = ListaEnlazada()
    for _ in range(num_hileras):
        dron_pos.insertar(0)
        dron_fin.insertar(False)
    for _ in range(instrucciones_pendientes.size):
        instrucciones_completadas.insertar(0)

    segundo = 1
    ultimo_riego = 0
    tabla_acciones = ""

    # Posicionamiento inicial
    for i in range(num_hileras):
        _set_at(dron_pos, i, 1)
    acciones_iniciales = [f"Adelante (H{i+1}P1)" for i in range(num_hileras)]
    tabla_acciones = _append_fila(tabla_acciones, segundo, *acciones_iniciales)

    def _instrucciones_restantes():
        c = 0
        n = instrucciones_completadas.primero
        while n:
            if n.dato == 0:
                c += 1
            n = n.siguiente
        return c

    while _instrucciones_restantes() > 0:
        segundo += 1

        dron_movido = ListaEnlazada()
        acciones = ListaEnlazada()
        for i in range(num_hileras):
            dron_movido.insertar(False)
            fin = _get_at(dron_fin, i).dato
            acciones.insertar("" if fin else "Esperar")

        # FASE 1: Movimiento
        for dron_idx in range(num_hileras):
            if _get_at(dron_fin, dron_idx).dato:
                continue
            objetivo = _buscar_instruccion_dron(instrucciones_pendientes, instrucciones_completadas, dron_idx)
            if not objetivo:
                continue
            _, planta_obj = objetivo

            movio = _get_at(dron_movido, dron_idx)
            pos = _get_at(dron_pos, dron_idx)
            if not movio.dato:
                if pos.dato < planta_obj:
                    pos.dato += 1
                    _actualizar_accion_dron(dron_idx, acciones, f"Adelante (H{dron_idx+1}P{pos.dato})")
                    movio.dato = True
                elif pos.dato > planta_obj:
                    pos.dato -= 1
                    _actualizar_accion_dron(dron_idx, acciones, f"Atras (H{dron_idx+1}P{pos.dato})")
                    movio.dato = True

        # FASE 2: Riego
        nodo_inst = instrucciones_pendientes.primero
        nodo_comp = instrucciones_completadas.primero
        hubo_riego = False

        while nodo_inst and not hubo_riego:
            if nodo_comp.dato == 0:
                h, p = nodo_inst.dato.split('-')
                hilera_num = int(h[1:])
                planta_num = int(p[1:])
                dron_idx = hilera_num - 1

                if 0 <= dron_idx < num_hileras and not _get_at(dron_fin, dron_idx).dato:
                    if _puede_regar(dron_idx, planta_num, dron_pos, dron_movido):
                        planta = buscar_planta(invernadero, hilera_num, planta_num)
                        if planta:
                            agua_total += planta.lt_agua
                            fertilizante_total += planta.gr_fertilizante
                            nodo_agua = _get_at(agua_por_dron, dron_idx)
                            nodo_fert = _get_at(fertilizante_por_dron, dron_idx)
                            if nodo_agua:
                                nodo_agua.dato += planta.lt_agua
                            if nodo_fert:
                                nodo_fert.dato += planta.gr_fertilizante
                        nodo_comp.dato = 1
                        _actualizar_accion_dron(dron_idx, acciones, "Regar")
                        ultimo_riego = segundo
                        hubo_riego = True
            nodo_inst = nodo_inst.siguiente
            nodo_comp = nodo_comp.siguiente

        # FASE 3: Marcar FIN
        for i in range(num_hileras):
            fin = _get_at(dron_fin, i)
            if not fin.dato and not _tiene_instrucciones_pendientes(instrucciones_pendientes, instrucciones_completadas, i):
                acc = _get_at(acciones, i)
                if acc.dato == "Esperar":
                    acc.dato = "FIN"
                    fin.dato = True

        tabla_acciones = _append_fila(
            tabla_acciones,
            segundo,
            *[_get_at(acciones, i).dato for i in range(num_hileras)]
        )

        if segundo > 100:
            break

    tiempo_total = ultimo_riego
    return tiempo_total, agua_total, fertilizante_total, tabla_acciones, agua_por_dron, fertilizante_por_dron

# --- Rutas Flask ---
@simulacion_bp.route('/simular', methods=['POST'])
def simular():
    data = getattr(current_app, 'DATA', None)
    if not data:
        flash('No hay datos cargados para simular', 'danger')
        return redirect(url_for('cargar.index'))

    nombre_invernadero = request.form.get('inv')
    nombre_plan = request.form.get('plan')
    if not nombre_invernadero or not nombre_plan:
        flash('Debes seleccionar un invernadero y un plan', 'danger')
        return redirect(url_for('cargar.index'))

    inv_obj = next((inv for inv in data.invernaderos_objetos if inv.nombre == nombre_invernadero), None)
    plan_obj = next((plan for plan in inv_obj.planes_riego if plan.nombre == nombre_plan), None) if inv_obj else None

    if not inv_obj or not plan_obj:
        flash('No se encontró el invernadero o el plan seleccionado', 'danger')
        return redirect(url_for('cargar.index'))
    
    tiempo_total, agua_total, fertilizante_total, tabla_acciones, agua_por_dron, fertilizante_por_dron = calcular_consumos(plan_obj, inv_obj)

    plan_obj.agua_por_dron = lista_enlazada_a_lista(agua_por_dron)
    plan_obj.fertilizante_por_dron = lista_enlazada_a_lista(fertilizante_por_dron)

    return render_template(
        'reportes.html',
        invernadero=inv_obj,
        plan=plan_obj,
        tiempo_total=tiempo_total,
        agua_total=agua_total,
        fertilizante_total=fertilizante_total,
        tabla_acciones=tabla_acciones
    )

@simulacion_bp.route('/reporte_completo')
def reporte_completo():
    data = getattr(current_app, 'DATA', None)
    if not data:
        flash('No hay datos cargados para mostrar el reporte', 'danger')
        return redirect(url_for('cargar.index'))

    invernaderos = data.invernaderos_objetos
    for inv in invernaderos:
        for plan in inv.planes_riego:
            tiempo_total, agua_total, fertilizante_total, tabla_acciones, agua_por_dron, fertilizante_por_dron = calcular_consumos(plan, inv)
            plan.estadisticas = {
                'tiempo_total': tiempo_total,
                'agua_total': agua_total,
                'fertilizante_total': fertilizante_total,
                'recargas': 0 
            }
            plan.tabla_acciones = tabla_acciones
            plan.agua_por_dron = lista_enlazada_a_lista(agua_por_dron)
            plan.fertilizante_por_dron = lista_enlazada_a_lista(fertilizante_por_dron)

    return render_template(
        'reporte_completo.html',
        invernaderos=invernaderos
    )
