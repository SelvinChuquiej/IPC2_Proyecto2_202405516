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
    
    tiempo_total, agua_total, fertilizante_total, tabla_acciones, agua_por_dron, fertilizante_por_dron, drones_asignados = calcular_consumos(plan_obj, inv_obj)

    # Convertir ListaEnlazada a lista de valores (solo para mostrar, no para lógica) 
    def lista_enlazada_a_lista(le):
        valores = []
        nodo = le.primero
        while nodo:
            valores.append(nodo.dato)
            nodo = nodo.siguiente
        return valores
    
    # Crear lista de nombres de drones para la plantilla
    nombres_drones = ListaEnlazada()
    for dron_tuple in drones_asignados:
        dron, hilera_num = dron_tuple
        nombres_drones.insertar(dron.nombre)

    return render_template(
        'reportes.html',
        invernadero=inv_obj,
        plan=plan_obj,
        tiempo_total=tiempo_total,
        agua_total=agua_total,
        fertilizante_total=fertilizante_total,
        tabla_acciones=tabla_acciones,
        agua_por_dron=lista_enlazada_a_lista(agua_por_dron),
        fertilizante_por_dron=lista_enlazada_a_lista(fertilizante_por_dron),
        nombres_drones=lista_enlazada_a_lista(nombres_drones)
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

def _append_fila(tabla_acciones, segundo, acciones_drones):
    """
    Agregar fila a la tabla de acciones con número dinámico de drones
    acciones_drones: ListaEnlazada con las acciones de cada dron asignado
    """
    fila = f"<tr><td>{segundo} segundo</td>"
    for accion in acciones_drones:
        fila += f"<td>{accion}</td>"
    fila += "</tr>\n"
    return tabla_acciones + fila

# Helpers para trabajar con drones asignados dinámicamente
def _obtener_drones_asignados(invernadero):
    """
    Obtiene lista enlazada de drones asignados con sus hileras
    Retorna: ListaEnlazada de tuplas (dron, hilera_numero)
    """
    drones_asignados = ListaEnlazada()
    for hilera in invernadero.hileras:
        if hilera.dron_asignado is not None:
            drones_asignados.insertar((hilera.dron_asignado, hilera.numero))
    return drones_asignados

def _obtener_dron_por_hilera(drones_asignados, hilera_num):
    """
    Busca el dron asignado a una hilera específica
    Retorna: tupla (dron, posicion_en_lista) o None si no se encuentra
    """
    posicion = 0
    for dron_tuple in drones_asignados:
        dron, hilera = dron_tuple
        if hilera == hilera_num:
            return (dron, posicion)
        posicion += 1
    return None

def _obtener_posicion_dron_por_hilera(drones_asignados, hilera_num):
    """
    Obtiene la posición del dron en la lista de drones asignados basado en su hilera
    """
    posicion = 0
    for dron_tuple in drones_asignados:
        dron, hilera = dron_tuple
        if hilera == hilera_num:
            return posicion
        posicion += 1
    return -1

# Búsquedas y reglas de negocio
def _buscar_instruccion_dron(instrucciones_pendientes, instrucciones_completadas, hilera_num, drones_asignados):
    """Siguiente instrucción PENDIENTE (0) para esta hilera."""
    nodo_inst = instrucciones_pendientes.primero
    nodo_comp = instrucciones_completadas.primero
    while nodo_inst:
        partes = nodo_inst.dato.split('-')
        h = int(partes[0][1:])
        p = int(partes[1][1:])
        if h == hilera_num and nodo_comp.dato == 0:
            return (nodo_inst, p)
        nodo_inst = nodo_inst.siguiente
        nodo_comp = nodo_comp.siguiente
    return None

def _tiene_instrucciones_pendientes(instrucciones_pendientes, instrucciones_completadas, hilera_num):
    """¿Quedan instrucciones sin completar para esta hilera?"""
    nodo_inst = instrucciones_pendientes.primero
    nodo_comp = instrucciones_completadas.primero
    while nodo_inst:
        partes = nodo_inst.dato.split('-')
        h = int(partes[0][1:])
        if nodo_comp.dato == 0 and h == hilera_num:
            return True
        nodo_inst = nodo_inst.siguiente
        nodo_comp = nodo_comp.siguiente
    return False

def _actualizar_accion_dron(posicion_dron, acciones, nueva_accion):
    n = _get_at(acciones, posicion_dron)
    if n is not None:
        n.dato = nueva_accion

def _puede_regar(posicion_dron, planta_objetivo, dron_pos, dron_movido):
    pos = _get_at(dron_pos, posicion_dron).dato
    movio = _get_at(dron_movido, posicion_dron).dato
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
    # Obtener drones asignados dinámicamente
    drones_asignados = _obtener_drones_asignados(invernadero)
    num_drones = len(drones_asignados)
    
    # Totales generales
    tiempo_total = 0
    agua_total = 0
    fertilizante_total = 0
    # Totales por dron usando ListaEnlazada

    agua_por_dron = ListaEnlazada()
    fertilizante_por_dron = ListaEnlazada()

    for _ in range(num_drones):
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

    for i in range(num_drones):
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
    # Crear acciones iniciales dinámicamente
    acciones_iniciales = ListaEnlazada()
    posicion = 0
    for dron_tuple in drones_asignados:
        dron, hilera_num = dron_tuple
        _set_at(dron_pos, posicion, 1)
        acciones_iniciales.insertar(f"Adelante (H{hilera_num}P1)")
        posicion += 1
    tabla_acciones = _append_fila(tabla_acciones, segundo, acciones_iniciales)

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
        for i in range(num_drones):
            dron_movido.insertar(False)
            # Si ya terminó, no mostramos acción (queda celda vacía)
            fin = _get_at(dron_fin, i).dato
            acciones.insertar("" if fin else "Esperar")

        # FASE 1: Movimiento (máx 1 paso por dron, en orden del plan)
        posicion = 0
        for dron_tuple in drones_asignados:
            dron, hilera_num = dron_tuple
            # si ya terminó, saltar
            if _get_at(dron_fin, posicion).dato:
                posicion += 1
                continue
            objetivo = _buscar_instruccion_dron(instrucciones_pendientes, instrucciones_completadas, hilera_num, drones_asignados)
            if not objetivo:
                posicion += 1
                continue
            _, planta_obj = objetivo

            movio = _get_at(dron_movido, posicion)
            pos = _get_at(dron_pos, posicion)
            if not movio.dato:
                if pos.dato < planta_obj:
                    pos.dato += 1
                    _actualizar_accion_dron(posicion, acciones, f"Adelante (H{hilera_num}P{pos.dato})")
                    movio.dato = True
                elif pos.dato > planta_obj:
                    pos.dato -= 1
                    _actualizar_accion_dron(posicion, acciones, f"Atras (H{hilera_num}P{pos.dato})")
                    movio.dato = True
                # si ya está en la planta, no se mueve (espera a fase de riego)
            posicion += 1

        # FASE 2: Riego (máx 1 por segundo; en orden del plan)
        nodo_inst = instrucciones_pendientes.primero
        nodo_comp = instrucciones_completadas.primero
        hubo_riego = False

        while nodo_inst and not hubo_riego:
            if nodo_comp.dato == 0:
                h, p = nodo_inst.dato.split('-')
                hilera_num = int(h[1:])
                planta_num = int(p[1:])
                
                # Buscar la posición del dron para esta hilera
                posicion_dron = _obtener_posicion_dron_por_hilera(drones_asignados, hilera_num)
                if posicion_dron >= 0 and not _get_at(dron_fin, posicion_dron).dato:
                    if _puede_regar(posicion_dron, planta_num, dron_pos, dron_movido):
                        # Sumar consumos
                        planta = buscar_planta(invernadero, hilera_num, planta_num)
                        if planta:
                            agua_total += planta.lt_agua
                            fertilizante_total += planta.gr_fertilizante
                            # Usar ListaEnlazada para sumar consumos por dron
                            nodo_agua = _get_at(agua_por_dron, posicion_dron)
                            nodo_fert = _get_at(fertilizante_por_dron, posicion_dron)
                            if nodo_agua:
                                nodo_agua.dato += planta.lt_agua
                            if nodo_fert:
                                nodo_fert.dato += planta.gr_fertilizante
                        # Marcar instrucción
                        nodo_comp.dato = 1
                        _actualizar_accion_dron(posicion_dron, acciones, "Regar")
                        ultimo_riego = segundo
                        hubo_riego = True
            nodo_inst = nodo_inst.siguiente
            nodo_comp = nodo_comp.siguiente

        # FASE 3: Marcar FIN donde ya no hay pendientes (y acción quedó "Esperar")
        posicion = 0
        for dron_tuple in drones_asignados:
            dron, hilera_num = dron_tuple
            fin = _get_at(dron_fin, posicion)
            if not fin.dato and not _tiene_instrucciones_pendientes(instrucciones_pendientes, instrucciones_completadas, hilera_num):
                acc = _get_at(acciones, posicion)
                if acc.dato == "Esperar":
                    acc.dato = "FIN"
                    fin.dato = True
            posicion += 1

        # Agregar fila
        tabla_acciones = _append_fila(tabla_acciones, segundo, acciones)

        # Protección anti-infinito (por si el plan es imposible)
        if segundo > 100:
            break

    tiempo_total = ultimo_riego
    return tiempo_total, agua_total, fertilizante_total, tabla_acciones, agua_por_dron, fertilizante_por_dron, drones_asignados
