import unicodedata

from django.shortcuts import render
from .cola_circular import ColaCircular
from django.shortcuts import render, redirect
from django.utils import timezone
from .pila import Pila


# Puedes cambiar estos platos, textos y archivos por los reales.
MENUS = {
    "desayuno": [
        {
            "nombre": "Pan con Chicharrón",
            "imagen": "comedor/img/pan-con-chicharron.jpg",
            "descripcion": "Cerdo crujiente y jugoso con camote frito y zarza criolla.",
            "raciones": "Raciones: por confirmar",
            "platos_listos": 15,
            "raciones_meta": 30,
        },
        {
            "nombre": "Tamal",
            "imagen": "comedor/img/tamal.jpg",
            "descripcion": "Suave masa de maíz rellena de carne, cocida en hoja de plátano.",
            "raciones": "Raciones: por confirmar",
            "platos_listos": 15,
            "raciones_meta": 18,
        },
        {
            "nombre": "Patasca",
            "imagen": "comedor/img/patasca.jpg",
            "descripcion": "Contundente y reconfortante caldo de mote con carne y hierbabuena.",
            "raciones": "Raciones: por confirmar",
            "platos_listos": 5,
            "raciones_meta": 25,
        },
    ],
    
    "almuerzo": [
        {
            "nombre": "Arroz con Pollo",
            "imagen": "comedor/img/arroz-con-pollo.jpg",
            "descripcion": "Arroz acompañado de pollo.",
            "platos_listos": 25,
            "raciones_meta": 35,
        },
        {
            "nombre": "Lomo Saltado",
            "imagen": "comedor/img/lomo-saltado.jpg",
            "descripcion": "Trozos de carne salteados con papas fritas y verduras.",
            "raciones": "Raciones: por confirmar",
            "platos_listos": 35,
            "raciones_meta": 40,
        },
        {
            "nombre": "Ají de Gallina",
            "imagen": "comedor/img/aji-de-gallina.jpg",
            "descripcion": "Pechuga de pollo desmenuzada en salsa de ají amarillo.",
            "raciones": "Raciones: por confirmar",
            "platos_listos": 22,
            "raciones_meta": 25,
        },
    ],

    "merienda": [
        {
            "nombre": "Arroz con Leche",
            "imagen": "comedor/img/arroz-con-leche.jpg",
            "descripcion": "Cremoso postre de arroz perfumado con canela, clavo de olor y leche condensada.",
            "raciones": "Raciones: por confirmar",
            "platos_listos": 15,
            "raciones_meta": 50,
        },
        {
            "nombre": "Mazamorra Morada",
            "imagen": "comedor/img/mazamorra-morada.jpg",
            "descripcion": "Clásico postre criollo de maíz morado con fruta seca y un toque de canela.",
            "raciones": "Raciones: por confirmar",
            "platos_listos": 25,
            "raciones_meta": 50,
        },
        {
            "nombre": "Flan",
            "imagen": "comedor/img/flan.jpg",
            "descripcion": "Suave y sedoso postre de huevo y leche bañando en caramelo dorado.",
            "raciones": "Raciones: por confirmar",
            "platos_listos": 28,
            "raciones_meta": 42,
        },
    ]
}

HORARIOS = {
    "desayuno": "9:00 - 11:59",
    "almuerzo": "12:00 - 5:59",
    "merienda": "6:00 - 9:00",
}

TURNOS = {
    "desayuno": "Desayuno",
    "almuerzo": "Almuerzo",
    "merienda": "Merienda",
}

def inicio(request):
    turno = request.GET.get("turno", "almuerzo")
    if turno not in MENUS:
        turno = "almuerzo"

    menus_para_reserva = [
        {
            "clave": clave,
            "nombre": TURNOS[clave],
            "platos": platos,
        }
        for clave, platos in MENUS.items()
    ]
    platos_para_busqueda = [
        {
            "nombre": plato["nombre"],
            "descripcion": plato["descripcion"],
            "turno": clave,
            "turno_nombre": TURNOS[clave],
        }
        for clave, platos in MENUS.items()
        for plato in platos
    ]
    menu = MENUS[turno]
    busqueda = request.GET.get("q", "").strip()
    texto_busqueda = "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", busqueda.casefold())
        if unicodedata.category(caracter) != "Mn"
    )

    if texto_busqueda:
        menu = [
            item for item in menu
            if texto_busqueda in "".join(
                caracter
                for caracter in unicodedata.normalize(
                    "NFD",
                    f"{item['nombre']} {item['descripcion']}".casefold(),
                )
                if unicodedata.category(caracter) != "Mn"
            )
        ]

    if not menu:
        return render(request, "comedor/inicio.html", {
            "plato": None,
            "menu": [],
            "turnos": TURNOS,
            "turno_actual": turno,
            "turno_nombre": TURNOS[turno],
            "horario_actual": HORARIOS[turno],
            "busqueda": busqueda,
            "platos_para_busqueda": platos_para_busqueda,
            "menus_para_reserva": menus_para_reserva,
        })

    try:
        indice = int(request.GET.get("plato", 0))
    except ValueError:
        indice = 0

    indice %= len(menu)

    cola = ColaCircular()
    for item in menu:
        cola.encolar(item)

    for _ in range(indice):
        primero = cola.desencolar()
        cola.encolar(primero)

    # Pega este bloque aquí:
    plato_actual = cola.mostrar_frente().copy()

    platos_listos = plato_actual.get("platos_listos", 135)
    raciones_meta = plato_actual.get("raciones_meta", 180)

    plato_actual["platos_listos"] = platos_listos
    plato_actual["porcentaje_raciones"] = min(
        100,
        round(platos_listos / raciones_meta * 100),
    ) if raciones_meta > 0 else 0

    return render(request, "comedor/inicio.html", {
        "plato": plato_actual,
        "horario_actual": HORARIOS[turno],
        "menu": menu,
        "turnos": TURNOS,
        "turno_actual": turno,
        "turno_nombre": TURNOS[turno],
        "busqueda": busqueda,
        "platos_para_busqueda": platos_para_busqueda,
        "menus_para_reserva": menus_para_reserva,
        "indice": indice,
        "anterior": (indice - 1) % len(menu),
        "siguiente": (indice + 1) % len(menu),
    })


def principal(request):
    return render(request, "comedor/principal.html")




INVENTARIO = [
    {
        "id": "arroz",
        "nombre": "Arroz",
        "categoria": "Granos",
        "cantidad": 120,
        "unidad": "kg",
        "minimo": 40,
        "capacidad": 150,
        "lote": "#001",
        "imagen": "comedor/img/inventario/001.jpg",
    },
    {
        "id": "papa blanca",
        "nombre": "Papa blanca",
        "categoria": "Tubérculos",
        "cantidad": 500,
        "unidad": "kg",
        "minimo": 150,
        "capacidad": 600,
        "lote": "#002",
        "imagen": "comedor/img/inventario/002.jpg",
    },
    {
        "id": "cebolla",
        "nombre": "Cebolla roja",
        "categoria": "Verduras",
        "cantidad": 35,
        "unidad": "kg",
        "minimo": 50,
        "capacidad": 100,
        "lote": "#003",
        "imagen": "comedor/img/inventario/003.jpg",
    },
    {
        "id": "aceite",
        "nombre": "Aceite",
        "categoria": "Abarrotes",
        "cantidad": 18,
        "unidad": "L",
        "minimo": 8,
        "capacidad": 22,
        "lote": "#004",
        "imagen": "comedor/img/inventario/004.jpg",
    },
    {
        "id": "leche",
        "nombre": "Leche",
        "categoria": "Lácteos",
        "cantidad": 30,
        "unidad": "L",
        "minimo": 20,
        "capacidad": 40,
        "lote": "#005",
        "imagen": "comedor/img/inventario/005.jpg",
    },
    {
        "id": "papa amarilla",
        "nombre": "Papa amarilla",
        "categoria": "Tubérculos",
        "cantidad": 70,
        "unidad": "kg",
        "minimo": 80,
        "capacidad": 200,
        "lote": "#007",
        "imagen": "comedor/img/inventario/006.jpg",
    },
    {
        "id": "pollo",
        "nombre": "Pollo",
        "categoria": "Carnes",
        "cantidad": 35,
        "unidad": "kg",
        "minimo": 50,
        "capacidad": 100,
        "lote": "#007",
        "imagen": "comedor/img/inventario/007.jpg",
    },
    {
        "id": "huevo",
        "nombre": "Huevo",
        "categoria": "Abarrotes",
        "cantidad": 32,
        "unidad": "kg",
        "minimo": 18,
        "capacidad": 35,
        "lote": "#008",
        "imagen": "comedor/img/inventario/008.jpg",
    },
    {
        "id": "lomo",
        "nombre": "Lomo",
        "categoria": "Carnes",
        "cantidad": 40,
        "unidad": "kg",
        "minimo": 20,
        "capacidad": 30,
        "lote": "#009",
        "imagen": "comedor/img/inventario/009.jpg",
    },
    {
        "id": "tomate",
        "nombre": "Tomate",
        "categoria": "Verduras",
        "cantidad": 50,
        "unidad": "kg",
        "minimo": 40,
        "capacidad": 65,
        "lote": "#010",
        "imagen": "comedor/img/inventario/010.jpg",
    },
]


def inventario(request):
    categorias = ["Todos", "Granos", "Tubérculos", "Verduras", "Abarrotes", "Carnes", "Lácteos"]

    # El POST ocurre cuando se confirma un ajuste en la ventana.
    if request.method == "POST":
        if request.POST.get("accion") == "limpiar_historial":
            request.session["inventario_movimientos"] = []
            return redirect("inventario")

        # Desde aquí conserva tu código actual:
        producto_id = request.POST.get("producto_id")
        accion = request.POST.get("accion")

        try:
            delta = int(request.POST.get("delta", "0"))
        except ValueError:
            delta = 0

        # ...el resto del código que ya tenías...

        try:
            delta = int(request.POST.get("delta", "0"))
        except ValueError:
            delta = 0

        producto_base = next(
            (p for p in INVENTARIO if p["id"] == producto_id),
            None,
        )

        if producto_base and delta != 0 and accion == "ajustar":
            stock = request.session.get("inventario_stock", {})
            clave = producto_base["id"]

            cantidad_anterior = stock.get(clave, producto_base["cantidad"])
            cantidad_nueva = cantidad_anterior + delta

            # El stock no puede ser negativo.
            if cantidad_nueva >= 0:
                stock[clave] = cantidad_nueva
                request.session["inventario_stock"] = stock

                movimiento_nuevo = {
                    "producto": producto_base["nombre"],
                    "categoria": producto_base["categoria"],
                    "lote": producto_base["lote"],
                    "unidad": producto_base["unidad"],
                    "delta": delta,
                    "cambio": f"+{delta}" if delta > 0 else str(delta),
                    "tipo": "aumento" if delta > 0 else "disminucion",
                    "anterior": cantidad_anterior,
                    "nuevo": cantidad_nueva,
                    "fecha": timezone.localtime().strftime("%d/%m/%Y %H:%M"),
                }

                # Reconstruye la pila desde la sesión.
                # La sesión guarda una lista simple porque Django
                # no puede guardar directamente los nodos de Python.
                guardados = request.session.get("inventario_movimientos", [])
                pila = Pila()

                # Se guardan del más nuevo al más antiguo.
                # Para reconstruir la pila, se insertan al revés.
                for movimiento in reversed(guardados):
                    pila.push(movimiento)

                # El movimiento recién confirmado queda en la cima.
                pila.push(movimiento_nuevo)

                # pop() produce el orden LIFO: nuevo primero.
                historial = []
                while not pila.is_empty():
                    historial.append(pila.pop())

                request.session["inventario_movimientos"] = historial

        return redirect("inventario")

    stock_guardado = request.session.get("inventario_stock", {})
    todos_los_productos = []

    for producto_base in INVENTARIO:
        producto = producto_base.copy()
        producto["cantidad"] = stock_guardado.get(
            producto["id"],
            producto_base["cantidad"],
        )
        producto["critico"] = producto["cantidad"] <= producto["minimo"]
        producto["porcentaje"] = min(
            100,
            round(producto["cantidad"] / producto["capacidad"] * 100),
        )
        todos_los_productos.append(producto)

    categoria = request.GET.get("categoria", "Todos")
    if categoria not in categorias:
        categoria = "Todos"

    busqueda = request.GET.get("q", "").strip().lower()
    productos_visibles = todos_los_productos

    if categoria != "Todos":
        productos_visibles = [
            p for p in productos_visibles
            if p["categoria"] == categoria
        ]

    total_criticos = sum(
        1 for p in todos_los_productos if p["critico"]
    )

    historial_completo = request.session.get("inventario_movimientos", [])
    movimientos_por_pagina = 5
    total_paginas = max(
        1,
        (len(historial_completo) + movimientos_por_pagina - 1)
        // movimientos_por_pagina
    )

    try:
        pagina_actual = int(request.GET.get("pagina", 1))
    except ValueError:
        pagina_actual = 1

    pagina_actual = max(1, min(pagina_actual, total_paginas))

    inicio = (pagina_actual - 1) * movimientos_por_pagina
    movimientos_pagina = historial_completo[
        inicio:inicio + movimientos_por_pagina
    ]

    return render(request, "comedor/inventario.html", {
        "productos": productos_visibles,
        "categorias": categorias,
        "categoria_actual": categoria,
        "busqueda": request.GET.get("q", ""),
        "total_insumos": len(todos_los_productos),
        "total_criticos": total_criticos,
        "movimientos": movimientos_pagina,
        "pagina_actual": pagina_actual,
        "total_paginas": total_paginas,
        "pagina_anterior": max(1, pagina_actual - 1),
        "pagina_siguiente": min(total_paginas, pagina_actual + 1),
    })