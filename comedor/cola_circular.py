
class Nodo:
    def __init__ (self, dato):
        self.dato = dato
        self.sig = None

class ColaCircular:
    def __init__ (self):
        self.frente = None
        self.final = None

    def encolar (self, dato):
        nuevo = Nodo (dato)
        if (self.frente is None):
            self.frente = nuevo
            self.final = nuevo
        else:
            self.final.sig = nuevo
            self.final = nuevo
        self.final.sig = self.frente

    def desencolar (self):
        if (self.frente is None):
            return "COLA VACÍA"
        dato_e = self.frente.dato
        if (self.frente == self.final):
            self.frente = None
            self.final = None
        else:
            self.frente = self.frente.sig
            self.final.sig = self.frente
        return dato_e
    
    def buscar (self, valorB):
        p = self.frente
        while (p):
            if (p.dato == valorB):
                return p.dato
            if (p == self.final):
                break
            p = p.sig
        return None
    
    def mostrar (self):
        p = self.frente
        while (p):
            print (p.dato, end = ("  <==  "))
            if (p == self.final):
                break
            p = p.sig

    def mostrar_frente (self):
        if (self.frente is None):
            return "COLA VACÍA"
        return self.frente.dato