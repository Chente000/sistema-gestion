from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q # Importar Q para filtros complejos
from .models import PracticaProfesional # Asegúrate de que el modelo esté importado
from .forms import PracticaProfesionalForm # Asegúrate de que el formulario esté importado
from programacion.models import Carrera, semestre # Importar Carrera y semestre si los usas para filtros
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test
from administrador.permissions import PERMISSIONS

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.VIEW_PRACTICA), login_url='/no-autorizado/')
def practica_list(request):
    query = request.GET.get('q', '')
    carrera_id = request.GET.get('carrera')
    estado_filter = request.GET.get('estado')
    
    practicas = PracticaProfesional.objects.all().select_related('carrera_estudiante', 'semestre_estudiante') # Optimización

    if query:
        practicas = practicas.filter(
            Q(nombre_estudiante__icontains=query) |
            Q(cedula_estudiante__icontains=query) |
            Q(nombre_empresa__icontains=query) |
            Q(nombre_tutor_externo__icontains=query) |
            Q(objetivos_practica__icontains=query) |
            Q(actividades_especificas__icontains=query)
        )
    
    if carrera_id:
        practicas = practicas.filter(carrera_estudiante__id=carrera_id)
    
    if estado_filter:
        practicas = practicas.filter(estado=estado_filter)

    carreras = Carrera.objects.all().order_by('nombre')
    estados_choices = PracticaProfesional.ESTADO_CHOICES # Obtener las opciones de estado

    return render(request, 'practicas_list.html', {
        'practicas': practicas,
        'carreras': carreras,
        'estados_choices': estados_choices,
        'query': query,
        'filter_carrera_id': carrera_id,
        'filter_estado': estado_filter,
    })

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.ADD_PRACTICA), login_url='/no-autorizado/')
def practica_create(request):
    if request.method == 'POST':
        form = PracticaProfesionalForm(request.POST)
        if form.is_valid():
            practica = form.save(commit=False)
            # Puedes asignar el usuario que registra si lo necesitas
            # practica.registrado_por = request.user 
            practica.save()
            return redirect('practicas:practica_list')
    else:
        form = PracticaProfesionalForm()
    
    # Para la carga dinámica de semestres en el template
    carreras = Carrera.objects.all().order_by('nombre')
    semestres_all = semestre.objects.all().order_by('nombre') # Para el JS inicial

    return render(request, 'practica_create.html', {
        'form': form,
        'carreras': carreras, # Para el select de carrera
        'semestres_all': semestres_all, # Para la precarga de semestres en JS
    })

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.VIEW_PRACTICA), login_url='/no-autorizado/')
def practica_detail(request, pk):
    practica = get_object_or_404(PracticaProfesional, pk=pk)
    return render(request, 'practica_detail.html', {'practica': practica})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.CHANGE_PRACTICA), login_url='/no-autorizado/')
def practica_edit(request, pk):
    practica = get_object_or_404(PracticaProfesional, pk=pk)
    if request.method == 'POST':
        form = PracticaProfesionalForm(request.POST, instance=practica)
        if form.is_valid():
            form.save()
            return redirect('practicas:practica_detail', pk=practica.pk) # Redirigir a detalle
    else:
        form = PracticaProfesionalForm(instance=practica)
    
    # Para la carga dinámica de semestres en el template
    carreras = Carrera.objects.all().order_by('nombre')
    semestres_all = semestre.objects.all().order_by('nombre') 
    
    # Si la práctica ya tiene una carrera, pre-filtrar los semestres para el JS
    if practica.carrera_estudiante:
        semestres_all = semestre.objects.filter(carrera=practica.carrera_estudiante).order_by('nombre')

    return render(request, 'practica_edit.html', {
        'form': form, 
        'practica': practica, # Para el template
        'carreras': carreras,
        'semestres_all': semestres_all, # Para la precarga de semestres en JS
    })

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.DELETE_PRACTICA), login_url='/no-autorizado/')
def practica_delete(request, pk):
    practica = get_object_or_404(PracticaProfesional, pk=pk)
    if request.method == 'POST':
        practica.delete()
        return redirect('practicas:practica_list')
    return render(request, 'practica_delete.html', {'practica': practica})

# --- VISTAS API (REUTILIZACIÓN) ---
# Necesitarás la vista api_semestres_por_carrera de 'programacion.views'
# Asegúrate de que esta vista esté accesible. Podrías importarla directamente o
# si 'programacion.views' ya está en tu urls.py principal, puedes llamarla.
# Para este ejemplo, asumiremos que ya existe o la crearemos aquí para claridad.

# Si ya tienes esta vista en programacion/views.py y la estás usando en urls.py de programacion,
# no la necesitas duplicar aquí. Solo asegúrate de que el URL pattern sea correcto
# para que el fetch de JS pueda alcanzarla.
# Ejemplo de cómo se vería si la tuvieras que poner aquí:
# from programacion.models import semestre, Carrera # Asegúrate de que estén importados

# def api_semestres_por_carrera(request):
#     carrera_id = request.GET.get('carrera_id')
#     semestres_data = []
#     if carrera_id:
#         semestres = semestre.objects.filter(carrera__id=carrera_id).order_by('nombre')
#         for sem in semestres:
#             semestres_data.append({'id': sem.id, 'nombre': sem.nombre})
#     return JsonResponse(semestres_data, safe=False)
