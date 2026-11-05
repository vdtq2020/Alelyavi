
class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.sig = None


class Pila:
    def __init__(self):
        self.cabecera = None

    def is_empty(self):
        return self.cabecera is None

    def push(self, dato):
        nuevo = Nodo(dato)
        nuevo.sig = self.cabecera
        self.cabecera = nuevo

    def peek(self):
        if self.is_empty():
            print("La Lista está Vacía.")
            return None
        return self.cabecera.dato

    def pop(self):
        if self.is_empty():
            print("La Lista está Vacía.")
            return None
        c_e = self.cabecera.dato
        self.cabecera = self.cabecera.sig
        return c_e

    def size(self):
        cont = 0
        p = self.cabecera
        while p:
            p = p.sig
            cont += 1
        return cont

    def mostrar(self):
        p = self.cabecera
        while p:
            print(p.dato, end=" ")
            p = p.sig
        print()