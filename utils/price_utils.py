from word2number import w2n

def correccion_precio(texto):
    try:
        # Eliminar posibles comas o puntos mal interpretados por el motor de voz
        texto_sin_comas = texto.replace(",", "").replace(".", "")
        try:
            # Intentar convertir texto en palabras a número
            precio = w2n.word_to_num(texto_sin_comas)
        except ValueError:
            # Si falla, intenta convertirlo como entero o flotante explícitamente
            if '.' in texto or 'punto' in texto:
                # Si incluye punto decimal, lo convierte en flotante
                precio = float(texto.replace('punto', '.'))
            else:
                # Sino, lo convierte en un entero
                precio = int(texto_sin_comas)
        return precio
    except ValueError:
        raise ValueError(f"El texto '{texto}' no se puede convertir en un precio válido.") 