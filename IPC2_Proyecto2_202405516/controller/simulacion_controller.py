from flask import Blueprint, request, redirect, url_for, flash, current_app, render_template

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
        if inv.nombre == nombre_invernadero:
            inv_obj = inv
            break

    # Buscar Plan
    plan_obj = None
    if inv_obj:
        for plan in inv_obj.planes_riego:
            if plan.nombre == nombre_plan:
                plan_obj = plan
                break

    if not inv_obj or not plan_obj:
        flash('No se encontró el invernadero o el plan seleccionado', 'danger')
        return redirect(url_for('cargar.index'))
    
    tiempo_optimo = getattr(plan_obj, 'tiempo_optimo', 0)
    agua_total = getattr(plan_obj, 'agua_total', 0)
    fert_total = getattr(plan_obj, 'fert_total', 0)

    return render_template('reportes.html', invernadero=inv_obj, plan=plan_obj, tiempo_optimo=tiempo_optimo, agua_total=agua_total, fert_total=fert_total)

def simulacion():
    return None