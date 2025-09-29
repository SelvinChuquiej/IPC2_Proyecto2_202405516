import xml.etree.ElementTree as ET

def crear_salida_xml(lista_invernaderos, ruta):
    root = ET.Element("datosSalida")
    lista_tag = ET.SubElement(root, "listaInvernaderos")
    nodo_inv = lista_invernaderos.primero
    while nodo_inv:
        inv = nodo_inv.dato
        inv_tag = ET.SubElement(lista_tag, "invernadero", {"nombre": inv.nombre})
        nodo_plan = inv.planes_riego.primero
        while nodo_plan:
            plan = nodo_plan.dato
            plan_tag = ET.SubElement(inv_tag, "plan", {"nombre": plan.nombre})

            # Estadísticas del plan
            ET.SubElement(plan_tag, "tiempoOptimoSegundos").text = str(getattr(plan, "tiempo_total", ""))
            ET.SubElement(plan_tag, "aguaRequeridaLitros").text = str(getattr(plan, "agua_total", ""))
            ET.SubElement(plan_tag, "fertilizanteRequeridoGramos").text = str(getattr(plan, "fertilizante_total", ""))

            # Eficiencia de drones
            eficiencia_tag = ET.SubElement(plan_tag, "eficienciaDronesRegadores")
            if hasattr(inv, "drones") and hasattr(plan, "agua_por_dron") and hasattr(plan, "fertilizante_por_dron"):
                nodo_dron = inv.drones.primero
                idx = 0
                while nodo_dron:
                    dron = nodo_dron.dato
                    litros = plan.agua_por_dron[idx] if idx < len(plan.agua_por_dron) else 0
                    gramos = plan.fertilizante_por_dron[idx] if idx < len(plan.fertilizante_por_dron) else 0
                    ET.SubElement(eficiencia_tag, "dron", {
                        "nombre": f"DR0{dron.id}",
                        "litrosAgua": str(litros),
                        "gramosFertilizante": str(gramos)
                    })
                    nodo_dron = nodo_dron.siguiente
                    idx += 1

            if hasattr(plan, "acciones_por_segundo"):
                instrucciones_tag = ET.SubElement(plan_tag, "instrucciones")
                nodo_segundo = plan.acciones_por_segundo.primero
                while nodo_segundo:
                    acciones_segundo = nodo_segundo.dato
                    tiempo_tag = ET.SubElement(instrucciones_tag, "tiempo", {"segundos": str(acciones_segundo.segundo)})
                    nodo_accion = acciones_segundo.acciones.primero
                    while nodo_accion:
                        accion_dron = nodo_accion.dato
                        ET.SubElement(tiempo_tag, "dron", {
                            "nombre": accion_dron.nombre_dron,
                            "accion": accion_dron.accion
                        })
                        nodo_accion = nodo_accion.siguiente
                    nodo_segundo = nodo_segundo.siguiente
            nodo_plan = nodo_plan.siguiente
        nodo_inv = nodo_inv.siguiente

    tree = ET.ElementTree(root)
    tree.write(ruta, encoding="utf-8", xml_declaration=True)