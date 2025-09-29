from flask import Blueprint, request, redirect, url_for, flash, current_app, render_template
from models.ListaEnlazada import ListaEnlazada

simulacion_bp = Blueprint('simulacion', __name__)

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

    # Buscar Invernadero
    inv_obj = None
    for inv in data.invernaderos_objetos:
        if inv.nombre == nombre_invernadero: inv_obj = inv; break

    # Buscar Plan
    plan_obj = None
    if inv_obj:
        for plan in inv_obj.planes_riego:
            if plan.nombre == nombre_plan: plan_obj = plan; break

    if not inv_obj or not plan_obj:
        flash('No se encontró el invernadero o el plan seleccionado', 'danger')
        return redirect(url_for('cargar.index'))
    
    tiempo_total, agua_total, fertilizante_total, tabla_acciones, agua_por_dron, fertilizante_por_dron = calcular_consumos(plan_obj, inv_obj)

    # Convertir ListaEnlazada a lista de valores (solo para mostrar, no para lógica) 
    def lista_enlazada_a_lista(le):
        valores = []
        nodo = le.primero
        while nodo:
            valores.append(nodo.dato)
            nodo = nodo.siguiente
        return valores

    return render_template(
        'reportes.html',
        invernadero=inv_obj,
        plan=plan_obj,
        tiempo_total=tiempo_total,
        agua_total=agua_total,
        fertilizante_total=fertilizante_total,
        tabla_acciones=tabla_acciones,
        agua_por_dron=lista_enlazada_a_lista(agua_por_dron),
        fertilizante_por_dron=lista_enlazada_a_lista(fertilizante_por_dron)
    )

# Helpers de listas enlazadas (para evitar repetir código)
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

def _append_fila(tabla_acciones, segundo, acc1, acc2, acc3, acc4):
    return (
        tabla_acciones
        + f"<tr><td>{segundo} segundo</td>"
        + f"<td>{acc1}</td><td>{acc2}</td><td>{acc3}</td><td>{acc4}</td></tr>\n"
    )

# Búsquedas y reglas de negocio
def _buscar_instruccion_dron(instrucciones_pendientes, instrucciones_completadas, dron_idx):
    """Siguiente instrucción PENDIENTE (0) para este dron (hilera = dron_idx+1)."""
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
    """¿Quedan instrucciones sin completar para la hilera = dron_idx+1?"""
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

# Simulación
def calcular_consumos(plan, invernadero):
    # Totales generales
    tiempo_total = 0
    agua_total = 0
    fertilizante_total = 0
    # Totales por dron usando ListaEnlazada

    agua_por_dron = ListaEnlazada()
    fertilizante_por_dron = ListaEnlazada()

    for _ in range(4):
        agua_por_dron.insertar(0)
        fertilizante_por_dron.insertar(0)

    # Instrucciones pendientes (validadas)
    instrucciones_pendientes = ListaEnlazada()
    for pedazo in plan.instrucciones_original.split(", "):
        inst = pedazo.strip()
        if plan.validar_formato(inst):
            instrucciones_pendientes.insertar(inst)

    # Estados (con ListaEnlazada)
    dron_pos = ListaEnlazada()             # posiciones: 0 -> antes de P1
    dron_fin = ListaEnlazada()             # True si ya no tiene pendientes
    instrucciones_completadas = ListaEnlazada()  # 0/1 por instrucción

    for i in range(4):
        dron_pos.insertar(0)
        dron_fin.insertar(False)
    for i in range(instrucciones_pendientes.size):
        instrucciones_completadas.insertar(0)

    # Control
    segundo = 0
    ultimo_riego = 0
    tabla_acciones = ""

    # Segundo 1: posicionamiento a P1
    segundo += 1
    _set_at(dron_pos, 0, 1)
    _set_at(dron_pos, 1, 1)
    _set_at(dron_pos, 2, 1)
    _set_at(dron_pos, 3, 1)
    tabla_acciones = _append_fila(tabla_acciones, segundo, "Adelante (H1P1)", "Adelante (H2P1)", "Adelante (H3P1)", "Adelante (H4P1)")

    # Bucle principal
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

        # Estructuras del segundo
        dron_movido = ListaEnlazada()
        acciones = ListaEnlazada()
        for i in range(4):
            dron_movido.insertar(False)
            # Si ya terminó, no mostramos acción (queda celda vacía)
            fin = _get_at(dron_fin, i).dato
            acciones.insertar("" if fin else "Esperar")

        # FASE 1: Movimiento (máx 1 paso por dron, en orden del plan)
        for dron_idx in range(4):
            # si ya terminó, saltar
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
                # si ya está en la planta, no se mueve (espera a fase de riego)

        # FASE 2: Riego (máx 1 por segundo; en orden del plan)
        nodo_inst = instrucciones_pendientes.primero
        nodo_comp = instrucciones_completadas.primero
        hubo_riego = False

        while nodo_inst and not hubo_riego:
            if nodo_comp.dato == 0:
                h, p = nodo_inst.dato.split('-')
                hilera_num = int(h[1:])
                planta_num = int(p[1:])
                dron_idx = hilera_num - 1

                if 0 <= dron_idx < 4 and not _get_at(dron_fin, dron_idx).dato:
                    if _puede_regar(dron_idx, planta_num, dron_pos, dron_movido):
                        # Sumar consumos
                        planta = buscar_planta(invernadero, hilera_num, planta_num)
                        if planta:
                            agua_total += planta.lt_agua
                            fertilizante_total += planta.gr_fertilizante
                            # Usar ListaEnlazada para sumar consumos por dron
                            nodo_agua = _get_at(agua_por_dron, dron_idx)
                            nodo_fert = _get_at(fertilizante_por_dron, dron_idx)
                            if nodo_agua:
                                nodo_agua.dato += planta.lt_agua
                            if nodo_fert:
                                nodo_fert.dato += planta.gr_fertilizante
                        # Marcar instrucción
                        nodo_comp.dato = 1
                        _actualizar_accion_dron(dron_idx, acciones, "Regar")
                        ultimo_riego = segundo
                        hubo_riego = True
            nodo_inst = nodo_inst.siguiente
            nodo_comp = nodo_comp.siguiente

        # FASE 3: Marcar FIN donde ya no hay pendientes (y acción quedó "Esperar")
        for i in range(4):
            fin = _get_at(dron_fin, i)
            if not fin.dato and not _tiene_instrucciones_pendientes(instrucciones_pendientes, instrucciones_completadas, i):
                acc = _get_at(acciones, i)
                if acc.dato == "Esperar":
                    acc.dato = "FIN"
                    fin.dato = True

        # Agregar fila
        tabla_acciones = _append_fila(
            tabla_acciones,
            segundo,
            _get_at(acciones, 0).dato,
            _get_at(acciones, 1).dato,
            _get_at(acciones, 2).dato,
            _get_at(acciones, 3).dato
        )

        # Protección anti-infinito (por si el plan es imposible)
        if segundo > 100:
            break

    tiempo_total = ultimo_riego
    return tiempo_total, agua_total, fertilizante_total, tabla_acciones, agua_por_dron, fertilizante_por_dron
