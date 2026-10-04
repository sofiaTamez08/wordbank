import json
from pathlib import Path


# Página de inicio; desplegar pestañas
def menu_principal():
    print("\nWORD BANK")
    print("1. Inicio")
    print("2. Editar wordbank")
    print("3. Favoritos")
    print("4. Salir")

    opcion = input("\nSelecciona una opción: ").strip()

    return opcion


# Pestaña de inicio
def home(wordbank):
    palabra = input(
        "¿Qué palabra quieres buscar? (0 para volver): ").strip().lower()

    if palabra == "0":
        return

    # Buscar palabra en el json
    palabra = buscar_clave_palabra(wordbank, palabra)
    if palabra in wordbank["palabras"]:
        print("Palabra encontrada")

        while True:
            mostrar_menu()

            opcion = input("Selecciona una opción: ").strip()

            match opcion:
                case "1":
                    print("Sinónimos: ")
                    mostrar_sinonimos(wordbank, palabra)

                case "2":
                    print("Alternativas: ")
                    mostrar_alternativas(wordbank, palabra)

                case "3":
                    mostrar_contraste(wordbank, palabra)

                case "4":
                    return

                case _:
                    print("Opción inválida")
    else:
        print("Palabra no disponible en el wordbank")


def mostrar_menu():
    print("\n¿Qué deseas consultar?")
    print("1. Sinónimos")
    print("2. Alternativas")
    print("3. Antónimos / Contraste")
    print("4. Volver")


def obtener_texto(item):
    return item if isinstance(item, str) else item["texto"]


def normalizar_comparacion(texto):
    return texto.strip().casefold()


def buscar_clave_palabra(wordbank, texto):
    if texto in wordbank["palabras"]:
        return texto
    for palabra in wordbank["palabras"]:
        if normalizar_comparacion(palabra) == normalizar_comparacion(texto):
            return palabra
    return texto


# Revisión de duplicados
def preparar_items(entrada, existentes):
    conocidos = {normalizar_comparacion(
        obtener_texto(item)) for item in existentes}
    nuevos = []
    duplicados = 0
    for texto in entrada.split(","):
        texto = texto.strip()
        if not texto:
            continue
        clave = normalizar_comparacion(texto)
        if clave in conocidos:
            duplicados += 1
        else:
            nuevos.append({"texto": texto, "favorito": False})
            conocidos.add(clave)
    return nuevos, duplicados

# Mensaje con elementos guardados y duplicados omitidos


def mensaje_items_guardados(cantidad, duplicados):
    return f"{cantidad} elementos guardados. Duplicados omitidos: {duplicados}."


def migrar_wordbank(wordbank):
    cambiado = False
    for datos in wordbank["palabras"].values():
        for categoria in ("sinonimos", "contraste"):
            for indice, item in enumerate(datos[categoria]):
                if isinstance(item, str):
                    datos[categoria][indice] = {
                        "texto": item, "favorito": False}
                    cambiado = True
    return cambiado


def mostrar_sinonimos(wordbank, palabra):
    sinonimos = wordbank["palabras"][palabra]["sinonimos"]

    for sinonimo in sinonimos:
        print(obtener_texto(sinonimo))

# Mostrar alternativas incorporando los filtros


def mostrar_alternativas(wordbank, palabra):
    while True:
        print("\n ALTERNATIVAS")
        print("1. Todas")
        print("2. Por emoción")
        print("3. Por lenguaje corporal")
        print("4. Volver")
        print("\n")

        opcion = input("Selecciona una opción: ").strip()

        match opcion:
            case "1":
                filtrar_alternativas(wordbank, palabra)

            case "2":
                emociones = obtener_emociones(wordbank, palabra)

                if not emociones:
                    print("No hay emociones disponibles.")
                    continue

                print("Emociones disponibles:")

                for i, emocion in enumerate(emociones, start=1):
                    print(f"{i}. {emocion}")

                while True:
                    try:
                        opcion = int(
                            input("Selecciona una emoción (0 para volver): "))
                    except ValueError:
                        print("Introduce un número válido.")
                        continue

                    if 0 <= opcion <= len(emociones):
                        break
                    print("Opción fuera de rango.")

                if opcion == 0:
                    continue
                emocion_elegida = emociones[opcion - 1]

                while True:
                    lenguaje = input(
                        "¿Solo mostrar lenguaje corporal? (s/n): "
                    ).strip().lower()
                    if lenguaje in ("s", "n"):
                        break
                    print("Responde s o n.")

                if lenguaje == "s":
                    filtrar_alternativas(
                        wordbank,
                        palabra,
                        emocion=emocion_elegida,
                        solo_lenguaje_corporal=True
                    )

                else:
                    filtrar_alternativas(
                        wordbank,
                        palabra,
                        emocion=emocion_elegida
                    )

            case "3":
                filtrar_alternativas(
                    wordbank,
                    palabra,
                    solo_lenguaje_corporal=True
                )
            case "4":
                return

            case _:
                print("Opción no válida")

# Filtro de emociones


def obtener_emociones(wordbank, palabra):
    alternativas = wordbank["palabras"][palabra]["alternativas"]
    emociones = []

    for alternativa in alternativas:
        for emocion in alternativa["emociones"]:
            if emocion not in emociones:
                emociones.append(emocion)

    return emociones


def filtrar_alternativas(wordbank, palabra, emocion=None, solo_lenguaje_corporal=False):
    alternativas = wordbank["palabras"][palabra]["alternativas"]

    for alternativa in alternativas:

        cumple_emocion = True
        cumple_lenguaje = True

        if emocion is not None:
            cumple_emocion = emocion in alternativa["emociones"]

        if solo_lenguaje_corporal:
            cumple_lenguaje = alternativa["lenguaje_corporal"]

        if cumple_emocion and cumple_lenguaje:
            print(alternativa["texto"])


def mostrar_contraste(wordbank, palabra):
    contrastes = wordbank["palabras"][palabra]["contraste"]

    for contraste in contrastes:
        print(obtener_texto(contraste))


# Pestaña para editar/añadir palabras
def editar_wordbank(wordbank):
    while True:
        print("\nEDITAR WORDBANK")
        print("1. Agregar palabra")
        print("2. Editar palabra existente")
        print("3. Volver")

        opcion = input("\nSelecciona una opción:").strip()

        match opcion:
            case "1":
                agregar_palabra(wordbank)

            case "2":
                editar_palabra_existente(wordbank)

            case "3":
                return

            case _:
                print("Opción inválida")


def guardar_wordbank(wordbank):
    ruta = Path(__file__).resolve().with_name("wordbank.json")
    ruta_temporal = Path(__file__).resolve().with_name("wordbank_temp.json")

    try:
        with open(ruta_temporal, "w", encoding="utf-8") as archivo:
            json.dump(
                wordbank,
                archivo,
                ensure_ascii=False,
                indent=4
            )

        ruta_temporal.replace(ruta)
        return True

    except (OSError, TypeError, ValueError):
        print("No se pudieron guardar los cambios.")
        return False


def agregar_palabra(wordbank):
    palabra = input("Nueva palabra: ").strip()

    if not palabra or palabra == "0":
        print("Escribe una palabra no vacía y distinta de 0.")
        return

    if buscar_clave_palabra(wordbank, palabra) in wordbank["palabras"]:
        print("Esa palabra ya existe en el wordbank.")
        return

    wordbank["palabras"][palabra] = {
        "sinonimos": [],
        "alternativas": [],
        "contraste": []
    }

    if not guardar_wordbank(wordbank):
        del wordbank["palabras"][palabra]
        return

    print(f'"{palabra}" fue guardada correctamente.')


def agregar_sinonimos(wordbank, palabra):
    entrada = input("Sinónimos: ")

    existentes = wordbank["palabras"][palabra]["sinonimos"]
    sinonimos, duplicados = preparar_items(entrada, existentes)

    if not sinonimos:
        print("No hay sinónimos nuevos para guardar.")
        return

    anteriores = existentes.copy()
    existentes.extend(sinonimos)

    if not guardar_wordbank(wordbank):
        existentes[:] = anteriores
        return
    print(mensaje_items_guardados(len(sinonimos), duplicados))


def agregar_contraste(wordbank, palabra):
    entrada = input("Antónimos: ")

    existentes = wordbank["palabras"][palabra]["contraste"]
    contrastes, duplicados = preparar_items(entrada, existentes)

    if not contrastes:
        print("No hay antónimos nuevos para guardar.")
        return

    anteriores = existentes.copy()
    existentes.extend(contrastes)

    if not guardar_wordbank(wordbank):
        existentes[:] = anteriores
        return
    print(mensaje_items_guardados(len(contrastes), duplicados))


# Permitir agregar alternativas (1 a 1) especificando los filtros a los que corresponde
def agregar_alternativa(wordbank, palabra):
    while True:
        texto = input("Nueva alternativa: ").strip()

        if not texto:
            print("La alternativa no puede quedar vacía.")
            continue

        if any(normalizar_comparacion(item["texto"]) == normalizar_comparacion(texto)
               for item in wordbank["palabras"][palabra]["alternativas"]):
            print("La alternativa ya existe.")
            return

        emociones_input = input(
            "Emociones: "
        ).strip()

        emociones = []
        for emocion in emociones_input.split(","):
            emocion = emocion.strip().lower()
            if emocion and emocion not in emociones:
                emociones.append(emocion)

        while True:
            respuesta = input(
                "¿Es lenguaje corporal? (s/n): "
            ).strip().lower()

            if respuesta == "s":
                lenguaje_corporal = True
                break

            elif respuesta == "n":
                lenguaje_corporal = False
                break

            else:
                print("Escribe 's' o 'n'")

        nueva_alternativa = {
            "texto": texto,
            "emociones": emociones,
            "lenguaje_corporal": lenguaje_corporal,
            "favorito": False
        }

        wordbank["palabras"][palabra]["alternativas"].append(
            nueva_alternativa
        )

        if not guardar_wordbank(wordbank):
            wordbank["palabras"][palabra]["alternativas"].pop()
            return
        print("Alternativa guardada correctamente.")

        while True:
            otra = input(
                "¿Agregar otra alternativa? (s/n): "
            ).strip().lower()

            if otra == "s":
                break

            elif otra == "n":
                return

            else:
                print("Escribe solo 's' o 'n'")


# Editar palabra para agregar sinonimos / alternativas / antónimos
def editar_palabra_existente(wordbank):
    palabra = input(
        "¿Qué palabra quieres editar? "
    ).strip().lower()

    palabra = buscar_clave_palabra(wordbank, palabra)
    if palabra not in wordbank["palabras"]:
        print("Esa palabra no existe en el wordbank.")
        return

    while True:
        print(f'\nEDITANDO: "{palabra}"')
        print("1. Agregar sinónimos")
        print("2. Agregar alternativa")
        print("3. Agregar contraste")
        print("4. Volver")

        opcion = input("\nSelecciona una opción: ").strip()

        match opcion:
            case "1":
                agregar_sinonimos(wordbank, palabra)

            case "2":
                agregar_alternativa(wordbank, palabra)

            case "3":
                agregar_contraste(wordbank, palabra)

            case "4":
                return

            case _:
                print("Opción no válida")


# Desplegar las palabras que tienen favoritos
def mostrar_favoritos(wordbank):
    palabras_favoritos = []

    for palabra, datos in wordbank["palabras"].items():
        if any(
            isinstance(item, dict) and item.get("favorito") is True
            for item in datos["alternativas"]
        ):
            palabras_favoritos.append(palabra)

    if not palabras_favoritos:
        print("\nTodavía no tienes favoritos.")
        return

    while True:
        print("\nFAVORITOS")

        for i, palabra in enumerate(palabras_favoritos, start=1):
            print(f"{i}. {palabra}")

        print("0. Volver")

        opcion = input("Selecciona una palabra: ").strip()

        if opcion == "0":
            return

        try:
            indice = int(opcion) - 1
        except ValueError:
            print("Opción inválida.")
            continue

        if 0 <= indice < len(palabras_favoritos):
            palabra_elegida = palabras_favoritos[indice]
            mostrar_favoritos_palabra(wordbank, palabra_elegida)

        else:
            print("Opción inválida.")


# Desplegar las opciones favoritas de esa palabra (alternativas)
def mostrar_favoritos_palabra(wordbank, palabra):
    print(f"\nFAVORITOS — {palabra.upper()}")

    favoritos = [
        item for item in wordbank["palabras"][palabra]["alternativas"]
        if isinstance(item, dict) and item.get("favorito") is True
    ]

    if not favoritos:
        print("No hay favoritos para esta palabra.")
        return

    for i, item in enumerate(favoritos, start=1):
        print(f'{i}. {item["texto"]}')


# Activar o desactivar favorito
def cambiar_favorito(wordbank, palabra, indice):
    alternativas = wordbank["palabras"][palabra]["alternativas"]

    if type(indice) is not int or not 0 <= indice < len(alternativas):
        print("Índice de alternativa inválido.")
        return

    alternativa = alternativas[indice]

    favorito_anterior = alternativa["favorito"]

    alternativa["favorito"] = not alternativa["favorito"]

    if not guardar_wordbank(wordbank):
        alternativa["favorito"] = favorito_anterior
        print("No se pudo guardar el cambio en favorito.")


def validar_wordbank(wordbank):
    if not isinstance(wordbank, dict):
        raise ValueError("El wordbank debe ser un diccionario.")

    palabras = wordbank.get("palabras")

    if not isinstance(palabras, dict):
        raise ValueError("Falta el diccionario 'palabras'.")

    for palabra, datos in palabras.items():
        if not isinstance(datos, dict):
            raise ValueError(f"Datos inválidos para {palabra}.")

        for categoria in ("sinonimos", "alternativas", "contraste"):
            items = datos.get(categoria)

            if not isinstance(items, list):
                raise ValueError(
                    f"Falta la lista {categoria} de {palabra}."
                )

            for item in items:
                # Permite strings antiguos en sinónimos y contraste
                if categoria != "alternativas" and isinstance(item, str):
                    continue

                if not isinstance(item, dict):
                    raise ValueError(
                        f"Elemento inválido en {palabra}: {categoria}."
                    )

                if not isinstance(item.get("texto"), str):
                    raise ValueError(
                        f"Texto inválido en {palabra}: {categoria}."
                    )

                if categoria == "alternativas":
                    emociones = item.get("emociones")

                    if (
                        not isinstance(emociones, list)
                        or not all(isinstance(e, str) for e in emociones)
                    ):
                        raise ValueError(
                            f"Emociones inválidas en {palabra}."
                        )

                    if type(item.get("lenguaje_corporal")) is not bool:
                        raise ValueError(
                            f"Lenguaje corporal inválido en {palabra}."
                        )

                    if type(item.get("favorito")) is not bool:
                        raise ValueError(
                            f"Favorito inválido en {palabra}."
                        )


def cargar_wordbank():
    ruta = Path(__file__).resolve().with_name("wordbank.json")
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            wordbank = json.load(archivo)
    except FileNotFoundError:
        ruta_default = ruta.with_name("wordbank_default.json")
        try:
            with open(ruta_default, "r", encoding="utf-8") as archivo:
                wordbank = json.load(archivo)
            validar_wordbank(wordbank)
            # Exclusive creation never replaces an existing personal file,
            # including one created by another process while we read defaults.
            try:
                with open(ruta, "x", encoding="utf-8") as archivo:
                    json.dump(wordbank, archivo, ensure_ascii=False, indent=4)
            except FileExistsError:
                with open(ruta, "r", encoding="utf-8") as archivo:
                    wordbank = json.load(archivo)
        except (OSError, ValueError) as error:
            raise ValueError(
                f"No se pudo inicializar wordbank.json: {error}") from error
    except (OSError, ValueError) as error:
        # Never offer an empty editable bank in place of an unreadable file.
        raise ValueError(
            f"No se pudo cargar wordbank.json: {error}") from error

    validar_wordbank(wordbank)
    migrar_wordbank(wordbank)
    return wordbank


def main():

    try:
        wordbank = cargar_wordbank()
    except ValueError as error:
        print(error)
        return

    while True:
        opcion = menu_principal()

        match opcion:
            case "1":
                home(wordbank)

            case "2":
                editar_wordbank(wordbank)

            case "3":
                mostrar_favoritos(wordbank)

            case "4":
                print("Hasta luego")
                return

            case _:
                print("Opción inválida")


if __name__ == "__main__":
    main()
