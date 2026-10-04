"""CustomTkinter screens and callbacks for the Word Bank desktop app."""

from tkinter import messagebox

import customtkinter as ctk

from main import (
    buscar_clave_palabra,
    cargar_wordbank,
    guardar_wordbank,
    mensaje_items_guardados,
    normalizar_comparacion,
    obtener_texto,
    preparar_items,
)

PAPER = "#FAF8F6"
SURFACE = "#DEDAD2"
INK = "#585551"
MUTED = "#7D766E"
ACCENT = "#4F4034"
BORDER = "#D2CCC4"
HEART = "#A33F34"
HEART_OFF = "#B3A99D"
SERIF = "Hoefler Text"
SANS = "Helvetica"

PRIMARY_BUTTON_STYLE = {
    "fg_color": ACCENT,
    "hover_color": "#6F6259",
    "text_color": "#FAF8F2",
    "border_width": 0,
}

try:
    wordbank = cargar_wordbank()
except ValueError as error:
    messagebox.showerror("No se pudo abrir Word Bank", str(error))
    raise SystemExit(1) from error

ctk.set_appearance_mode("light")


def paper_frame(parent, **options):
    defaults = dict(fg_color="transparent", corner_radius=0)
    defaults.update(options)
    return ctk.CTkFrame(parent, **defaults)


def paper_scroll(parent, **options):
    defaults = dict(fg_color=PAPER, corner_radius=0,
                    scrollbar_button_color=BORDER,
                    scrollbar_button_hover_color=ACCENT)
    defaults.update(options)
    return ctk.CTkScrollableFrame(parent, **defaults)


def paper_label(parent, **options):
    text = options.get("text", "")
    defaults = dict(text_color=MUTED, font=(SANS, 14))
    if text[:1].isdigit():
        defaults.update(text_color=INK, font=(
            SERIF, 18), justify="left", anchor="w")
    elif text in ("Sinónimos", "Alternativas", "Antónimos / Contraste"):
        defaults.update(text_color=INK, font=(SERIF, 23))
    defaults.update(options)
    label = ctk.CTkLabel(parent, **defaults)
    if text[:1].isdigit():
        label.bind("<Configure>", lambda event: label.configure(
            wraplength=max(180, parent.winfo_width() - 80)
        ), add="+")
    return label


def paper_entry(parent, **options):
    defaults = dict(fg_color=SURFACE, text_color=INK,
                    placeholder_text_color=MUTED, border_color=BORDER,
                    border_width=1, corner_radius=4, height=40, font=(SANS, 15))
    defaults.update(options)
    return ctk.CTkEntry(parent, **defaults)


def paper_button(parent, **options):
    text = options.get("text", "")
    defaults = dict(
        fg_color=PAPER,
        hover_color=SURFACE,
        text_color=ACCENT,
        border_color=BORDER,
        border_width=1,
        corner_radius=2,
        height=34,
        font=(SANS, 14)
    )

    if text in ("♥", "♡"):

        defaults.update(
            fg_color="transparent",
            hover_color=SURFACE,
            border_width=0,
            text_color=HEART if text == "♥" else HEART_OFF,
            font=("Apple Symbols", 17),
            height=24
        )

    elif text.startswith(("›", "⌄")):
        defaults.update(fg_color="transparent", hover_color=SURFACE, border_width=0,
                        text_color=INK, anchor="w", height=44, font=(SERIF, 25))
        if "Filtrar" in text:
            defaults.update(font=(SERIF, 16), height=30, text_color=MUTED)
    elif text == "Limpiar filtros":
        defaults.update(fg_color="transparent", hover_color=SURFACE, border_width=0,
                        text_color=MUTED, height=28)
    defaults.update(options)
    return ctk.CTkButton(parent, **defaults)


def paper_checkbox(parent, **options):
    defaults = dict(fg_color=ACCENT, hover_color=BORDER, border_color=BORDER,
                    text_color=INK, checkmark_color=PAPER, border_width=1,
                    corner_radius=3, checkbox_width=16, checkbox_height=16,
                    font=(SERIF, 16), height=28)
    defaults.update(options)
    return ctk.CTkCheckBox(parent, **defaults)


def clear_content(content):
    for widget in content.winfo_children():
        widget.destroy()


def toggle_home_favorite(word, category, index, button, refresh=None):
    items = wordbank["palabras"][word][category]
    original_item = items[index]
    if isinstance(original_item, str):
        item = {"texto": original_item, "favorito": False}
        items[index] = item
    else:
        item = original_item

    had_favorite = "favorito" in item
    previous = item.get("favorito", False)
    item["favorito"] = not previous

    if guardar_wordbank(wordbank):
        button.configure(text="♥" if item["favorito"] else "♡",
                         text_color=HEART if item["favorito"] else HEART_OFF)
        if refresh is not None:
            refresh()
    else:
        if isinstance(original_item, str):
            items[index] = original_item
        elif had_favorite:
            item["favorito"] = previous
        else:
            del item["favorito"]
        messagebox.showerror(
            "Error al guardar", "No se pudo guardar el favorito. Intenta de nuevo.")


def add_favorite_button(frame, row, word, category, original_index, refresh=None):
    item = wordbank["palabras"][word][category][original_index]
    favorite = item.get("favorito", False) if isinstance(item, dict) else False
    button = paper_button(frame, text="♥" if favorite else "♡", width=32)
    button.configure(
        command=lambda: toggle_home_favorite(
            word, category, original_index, button, refresh)
    )
    frame.grid_columnconfigure(0, weight=1)
    button.grid(row=row, column=1, padx=8, pady=5, sticky="e")


def save_home_edit(word, category, index, text, emotions, body, message, refresh):
    items = wordbank["palabras"][word][category]
    text = text.strip()
    if not text:
        message.configure(text="El texto no puede quedar vacío.")
        return False
    if any(i != index and normalizar_comparacion(obtener_texto(item)) == normalizar_comparacion(text)
           for i, item in enumerate(items)):
        message.configure(text="Ya existe otro elemento con ese texto.")
        return False

    original = items[index]
    previous = original.copy() if isinstance(original, dict) else original
    item = original if isinstance(original, dict) else {
        "texto": original, "favorito": False}
    item["texto"] = text
    if category == "alternativas":
        tags = []
        for emotion in emotions:
            emotion = emotion.strip().lower()
            if emotion and emotion not in tags:
                tags.append(emotion)
        item["emociones"] = tags
        item["lenguaje_corporal"] = bool(body)
    items[index] = item
    if not guardar_wordbank(wordbank):
        if isinstance(original, dict):
            original.clear()
            original.update(previous)
        else:
            items[index] = original
        message.configure(text="No se pudo guardar. Intenta de nuevo.")
        return False
    refresh()
    return True


def delete_home_item(word, category, index, refresh):
    items = wordbank["palabras"][word][category]
    item = items[index]
    if not messagebox.askyesno("Eliminar elemento", f'¿Eliminar "{obtener_texto(item)}"?'):
        return
    items.pop(index)
    if not guardar_wordbank(wordbank):
        items.insert(index, item)
        messagebox.showerror("Error al guardar",
                             "No se pudo eliminar el elemento.")
        return
    refresh()


def open_home_editor(word, category, index, parent, refresh):
    """A modal editor keeps list indices stable while the user edits an item."""
    item = wordbank["palabras"][word][category][index]
    editor = ctk.CTkToplevel(parent.winfo_toplevel())
    editor.title("Editar elemento")
    editor.configure(fg_color=PAPER)
    editor.geometry("560x620" if category == "alternativas" else "560x280")
    editor.minsize(420, 260)
    editor.transient(parent.winfo_toplevel())
    editor.grid_columnconfigure(0, weight=1)
    editor.grid_rowconfigure(0, weight=1)
    fields = paper_scroll(editor)
    fields.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    fields.grid_columnconfigure(0, weight=1)
    paper_label(fields, text="Editar elemento", font=(
        SERIF, 23)).grid(row=0, column=0, pady=8)
    entry = paper_entry(fields)
    entry.insert(0, obtener_texto(item))
    entry.grid(row=1, column=0, pady=8, sticky="ew")
    boxes = []
    custom = None
    body = None
    if category == "alternativas":
        paper_label(fields, text="Emociones").grid(
            row=2, column=0, pady=8, sticky="w")
        emotion_frame = paper_frame(fields)
        emotion_frame.grid(row=3, column=0, sticky="ew")
        refresh_emotion_options(emotion_frame, boxes)
        selected = {e.strip().lower() for e in item["emociones"]}
        for emotion, checkbox in boxes:
            if emotion in selected:
                checkbox.select()
        custom = paper_entry(
            fields, placeholder_text="Agregar emoción nueva: alivio, nostalgia")
        custom.grid(row=4, column=0, pady=8, sticky="ew")
        body = paper_checkbox(fields, text="Lenguaje corporal")
        body.grid(row=5, column=0, pady=8, sticky="w")
        if item["lenguaje_corporal"]:
            body.select()
    message = paper_label(fields, text="", wraplength=440)
    message.grid(row=6, column=0, pady=8, sticky="ew")

    def save():
        emotions = [e for e, checkbox in boxes if checkbox.get()]
        if custom is not None:
            emotions += custom.get().split(",")
        if save_home_edit(word, category, index, entry.get(), emotions,
                          body.get() if body is not None else False, message, refresh):
            editor.destroy()

    actions = paper_frame(fields)
    actions.grid(row=7, column=0, pady=8)
    paper_button(actions, text="Guardar", command=save).grid(
        row=0, column=0, padx=4)
    paper_button(actions, text="Cancelar", command=editor.destroy).grid(
        row=0, column=1, padx=4)
    editor.wait_visibility()
    editor.grab_set()
    entry.focus_set()


def add_home_edit_controls(frame, row, word, category, index, refresh):
    actions = paper_frame(frame)
    actions.grid(row=row, column=2, padx=4, pady=4, sticky="e")
    paper_button(actions, text="Editar", width=64,
                 command=lambda: open_home_editor(word, category, index, frame, refresh)).grid(row=0, column=0, padx=3)
    paper_button(actions, text="Eliminar", width=70,
                 command=lambda: delete_home_item(word, category, index, refresh)).grid(row=0, column=1, padx=3)


def refresh_home_text_section(word, frame, toggle):
    clear_content(frame)
    toggle(word, frame)


def add_section_pencil(
    word,
    frame,
    header,
    arrow,
    title,
    toggle,
    parent,
    row
):
    frame.edit_mode = False

    pencil = paper_button(
        parent,
        text="✎",
        width=30,
        height=30,
        fg_color="transparent",
        border_width=0,
        text_color=MUTED,
        font=("Apple Symbols", 15)
    )

    pencil.grid(
        row=row,
        column=1,
        padx=(4, 8),
        pady=8,
        sticky="e"
    )

    def switch_mode():
        frame.edit_mode = not frame.edit_mode

        pencil.configure(
            text_color=ACCENT if frame.edit_mode else MUTED,
            fg_color=SURFACE if frame.edit_mode else "transparent"
        )

        if not frame.winfo_children():
            toggle(word, frame)

        elif title == "Alternativas":
            frame.refresh_results()

        else:
            refresh_home_text_section(
                word,
                frame,
                toggle
            )

        header.configure(text=title)

        if frame.winfo_ismapped():
            arrow.configure(text="⌃")
        else:
            arrow.configure(text="⌄")

    pencil.configure(command=switch_mode)


def navigate_home_synonym(target, entry, message, categories_frame):
    target = buscar_clave_palabra(wordbank, target)
    if target not in wordbank["palabras"]:
        return
    entry.delete(0, "end")
    entry.insert(0, target)
    search_word(entry, message, categories_frame)


def show_inline_items(word, category, parent):
    flow = paper_frame(parent, height=1)
    flow.grid(row=0, column=0, columnspan=3, padx=8, pady=4, sticky="ew")
    parent.grid_columnconfigure(0, weight=1)
    font = ctk.CTkFont(family=SERIF, size=18)
    last_width = None

    def arrange(event=None):
        nonlocal last_width
        width = flow.winfo_width()
        if width <= 1:
            width = max(100, parent.winfo_width() - 16)
        if width == last_width:
            return
        last_width = width
        scale = flow._get_widget_scaling()
        available = width / scale
        clear_content(flow)
        row = None
        used = 0

        for value in wordbank["palabras"][word][category]:
            text = obtener_texto(value).lower()
            needed = min(available, font.measure(text) + 24)
            if row is None or used + needed > available:
                row = paper_frame(flow, height=1)
                row.pack(fill="x", pady=3)
                used = 0

            item = paper_frame(row, height=1)
            item.pack(side="left", padx=(0, 18), anchor="n")

            label = paper_label(
                item,
                text=text,
                font=(SERIF, 18),
                text_color=INK,
                anchor="w",
                justify="left",
                wraplength=max(1, available - 24)
            )

            label.grid(
                row=0,
                column=0,
                sticky="w"
            )

            underline = ctk.CTkFrame(
                item,
                width=font.measure(text),
                height=1,
                corner_radius=0,
                fg_color="#E7E2DC"
            )

            underline.grid(
                row=1,
                column=0,
                sticky="ew",
                pady=(0, 3)
            )

            if category == "sinonimos" and not getattr(parent, "edit_mode", False):
                target = buscar_clave_palabra(wordbank, obtener_texto(value))
                navigate = getattr(parent, "navigate_synonym", None)
                if target in wordbank["palabras"] and navigate is not None:
                    label.configure(cursor="hand2")
                    label.bind("<Button-1>", lambda event,
                               key=target: navigate(key))
                    underline = ctk.CTkFrame(
                        item, width=1, height=1, corner_radius=0, fg_color=BORDER, cursor="hand2"
                    )
                    underline.grid(row=1, column=0, sticky="ew", pady=(0, 3))
                    underline.bind("<Button-1>", lambda event,
                                   key=target: navigate(key))
            used += needed

    flow.bind("<Configure>", arrange)
    arrange()


def toggle_sinonimos(word, sinonimos_frame):
    if sinonimos_frame.winfo_children():
        for widget in sinonimos_frame.winfo_children():
            widget.destroy()
        sinonimos_frame.grid_remove()
        return

    sinonimos_frame.grid()

    sinonimos = wordbank["palabras"][word]["sinonimos"]

    if not sinonimos:
        mensaje = paper_label(
            sinonimos_frame,
            text="No hay sinónimos disponibles."
        )
        mensaje.grid(
            row=0,
            column=0,
            padx=8,
            pady=8,
            sticky="w"
        )
        return

    if not getattr(sinonimos_frame, "edit_mode", False):
        show_inline_items(word, "sinonimos", sinonimos_frame)
        return

    for i, sinonimo in enumerate(sinonimos, start=1):
        sinonimo = obtener_texto(sinonimo)
        label = paper_label(
            sinonimos_frame,
            text=f"{i}. {sinonimo[:1].upper() + sinonimo[1:]}"
        )

        label.grid(
            row=i,
            column=0,
            padx=8,
            pady=5,
            sticky="w"
        )

        if getattr(sinonimos_frame, "edit_mode", False):
            add_home_edit_controls(sinonimos_frame, i, word, "sinonimos", i - 1,
                                   lambda: refresh_home_text_section(word, sinonimos_frame, toggle_sinonimos))


def filter_home_alternatives(word, selected_emotions, only_body):
    selected = {emotion.strip().lower() for emotion in selected_emotions}
    results = []
    for original_index, alternative in enumerate(
        wordbank["palabras"][word]["alternativas"]
    ):
        emotions = {emotion.strip().lower()
                    for emotion in alternative["emociones"]}
        matches_emotion = not selected or bool(selected.intersection(emotions))
        matches_body = not only_body or alternative["lenguaje_corporal"] == True
        if matches_emotion and matches_body:
            results.append((original_index, alternative))
    return results


def toggle_alternativas(word, alternativas_frame):
    if alternativas_frame.winfo_children():
        clear_content(alternativas_frame)
        alternativas_frame.grid_remove()
        return

    alternativas_frame.grid()
    alternativas_frame.grid_columnconfigure(0, weight=1)
    alternatives = wordbank["palabras"][word]["alternativas"]
    emotions = sorted({
        emotion.strip().lower()
        for alternative in alternatives
        for emotion in alternative["emociones"]
        if emotion.strip()
    })

    emotion_button = paper_button(
        alternativas_frame, text="› Filtrar por emociones"
    )
    emotion_button.grid(row=0, column=0, padx=8, pady=4, sticky="w")

    options_frame = paper_frame(alternativas_frame, fg_color="transparent")
    options_frame.grid(row=1, column=0, padx=8, pady=4, sticky="ew")
    options_frame.grid_remove()
    emotions_open = False

    def toggle_emotion_options():
        nonlocal emotions_open
        emotions_open = not emotions_open
        if emotions_open:
            options_frame.grid()
            emotion_button.configure(text="⌄ Filtrar por emociones")
        else:
            options_frame.grid_remove()
            emotion_button.configure(text="› Filtrar por emociones")

    emotion_button.configure(command=toggle_emotion_options)
    checkboxes = []

    body_checkbox = paper_checkbox(
        alternativas_frame, text="Solo lenguaje corporal")
    body_checkbox.grid(row=2, column=0, padx=8, pady=8, sticky="w")

    count = paper_label(alternativas_frame, text="")
    count.grid(row=4, column=0, padx=8, pady=4, sticky="w")
    results_frame = paper_frame(alternativas_frame, fg_color="transparent")
    results_frame.grid(row=5, column=0, sticky="ew")

    def wrap_results(event=None):
        # Measure the actual page width, reserving room for hearts/edit controls.
        width = results_frame.winfo_width() / results_frame._get_widget_scaling()
        controls = {}
        for widget in results_frame.winfo_children():
            column = int(widget.grid_info().get("column", 0))
            if column > 0:
                controls[column] = max(controls.get(column, 0),
                                       widget.winfo_reqwidth() / results_frame._get_widget_scaling() + 16)
        text_width = max(40, width - sum(controls.values()) - 24)
        for widget in results_frame.winfo_children():
            if hasattr(widget, "original_index"):
                widget.configure(wraplength=text_width)

    results_frame.bind("<Configure>", wrap_results)

    def update_results():
        clear_content(results_frame)
        selected = [emotion for emotion,
                    checkbox in checkboxes if checkbox.get()]
        results = filter_home_alternatives(
            word, selected, bool(body_checkbox.get()))
        results.sort(key=lambda pair: not pair[1].get("favorito", False))
        count.configure(text=f"{len(results)} resultados")

        if not results:
            label = paper_label(
                results_frame, text="No hay alternativas con estos filtros."
            )
            label.grid(row=0, column=0, padx=8, pady=8, sticky="w")
            return

        for number, (original_index, alternative) in enumerate(results, start=1):
            text = alternative["texto"]

            label = paper_label(
                results_frame,
                text=f"·  {text[:1].upper() + text[1:]}",
                font=(SERIF, 18),
                text_color=INK,
                wraplength=180,
                justify="left"
            )

            label.original_index = original_index

            label.grid(row=number - 1,
                       column=0,
                       padx=8,
                       pady=5,
                       sticky="w"
                       )
            add_favorite_button(
                results_frame, number - 1, word, "alternativas", original_index, update_results
            )
            if getattr(alternativas_frame, "edit_mode", False):
                add_home_edit_controls(results_frame, number - 1, word,
                                       "alternativas", original_index, refresh_after_change)
        results_frame.after_idle(wrap_results)

    def refresh_after_change():
        selected = {emotion for emotion,
                    checkbox in checkboxes if checkbox.get()}
        available = sorted(selected | {
            e.strip().lower() for a in wordbank["palabras"][word]["alternativas"]
            for e in a["emociones"] if e.strip()
        })
        clear_content(options_frame)
        checkboxes.clear()
        for i, emotion in enumerate(available):
            checkbox = paper_checkbox(
                options_frame, text=emotion, command=update_results)
            checkbox.grid(row=i // 3, column=i % 3, padx=8, pady=5, sticky="w")
            if emotion in selected:
                checkbox.select()
            checkboxes.append((emotion, checkbox))
        update_results()

    alternativas_frame.refresh_results = update_results

    def clear_filters():
        for emotion, checkbox in checkboxes:
            checkbox.deselect()
        body_checkbox.deselect()
        update_results()

    for i, emotion in enumerate(emotions):
        checkbox = paper_checkbox(
            options_frame, text=emotion, command=update_results
        )
        checkbox.grid(row=i // 3, column=i % 3, padx=8, pady=5, sticky="w")
        checkboxes.append((emotion, checkbox))

    body_checkbox.configure(command=update_results)
    clear_button = paper_button(
        alternativas_frame, text="Limpiar filtros", command=clear_filters
    )
    clear_button.grid(row=3, column=0, padx=8, pady=4, sticky="w")
    update_results()


def toggle_contraste(word, contraste_frame):
    if contraste_frame.winfo_children():
        for widget in contraste_frame.winfo_children():
            widget.destroy()
        contraste_frame.grid_remove()
        return

    contraste_frame.grid()

    contrastes = wordbank["palabras"][word]["contraste"]

    if not contrastes:
        mensaje = paper_label(
            contraste_frame,
            text="No hay contrastes disponibles."
        )

        mensaje.grid(
            row=0,
            column=0,
            padx=8,
            pady=8,
            sticky="w"
        )

        return

    if not getattr(contraste_frame, "edit_mode", False):
        show_inline_items(word, "contraste", contraste_frame)
        return

    for i, contraste in enumerate(contrastes, start=1):
        contraste = obtener_texto(contraste)
        label = paper_label(
            contraste_frame,
            text=f"{i}. {contraste[:1].upper() + contraste[1:]}"
        )

        label.grid(
            row=i,
            column=0,
            padx=8,
            pady=5,
            sticky="w"
        )

        if getattr(contraste_frame, "edit_mode", False):
            add_home_edit_controls(contraste_frame, i, word, "contraste", i - 1,
                                   lambda: refresh_home_text_section(word, contraste_frame, toggle_contraste))


def toggle_section_with_arrow(
    word,
    section_frame,
    section_button,
    arrow_button,
    section_name,
    toggle_function
):
    toggle_function(word, section_frame)
    section_button.configure(text=section_name)

    if section_frame.winfo_ismapped():
        arrow_button.configure(text="⌃")
    else:
        arrow_button.configure(text="⌄")


def create_home_section(parent, word, title, row, toggle):
    header = paper_frame(parent, fg_color="transparent")
    header.grid(row=row, column=0, columnspan=2, padx=8,
                pady=(8, 0), sticky="ew")
    header.grid_columnconfigure(0, weight=1)

    button = paper_button(
        header, text=title, fg_color="transparent", hover_color=SURFACE,
        border_width=0, corner_radius=0, text_color=INK,
        font=(SERIF, 26), anchor="w"
    )
    button.grid(row=0, column=0, sticky="ew")
    arrow = paper_button(
        header, text="⌄", width=30, height=30, fg_color="transparent",
        hover_color=SURFACE, border_width=0, text_color=MUTED,
        font=("Apple Symbols", 15)
    )
    arrow.grid(row=0, column=2, padx=(0, 4))
    divider = ctk.CTkFrame(header, height=1, fg_color=BORDER, corner_radius=0)
    divider.grid(row=1, column=0, columnspan=3, sticky="ew")

    section_frame = paper_frame(parent, fg_color="transparent")
    section_frame.grid(row=row + 1, column=0, columnspan=2,
                       padx=8, pady=4, sticky="ew")
    section_frame.grid_remove()
    add_section_pencil(word, section_frame, button,
                       arrow, title, toggle, header, 0)

    def toggle_section():
        toggle_section_with_arrow(
            word, section_frame, button, arrow, title, toggle)

    button.configure(command=toggle_section)
    arrow.configure(command=toggle_section)
    return section_frame


def search_word(entry, message, categories_frame):
    word = entry.get().strip().lower()

    clear_content(categories_frame)

    if not word:
        message.configure(
            text="Introduce una palabra."
        )
        return

    word = buscar_clave_palabra(wordbank, word)

    if word in wordbank["palabras"]:
        message.configure(
            text=f"Palabra encontrada: {word}"
        )

        title = paper_label(
            categories_frame,
            text=word.upper(),
            font=(SERIF, 44),
            text_color=INK
        )

        title.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=8,
            pady=(26, 28),
            sticky="ew"
        )

        categories_frame.grid_columnconfigure(0, weight=1)

        synonyms_frame = create_home_section(
            categories_frame, word, "Sinónimos", 1, toggle_sinonimos
        )
        synonyms_frame.navigate_synonym = lambda target: navigate_home_synonym(
            target, entry, message, categories_frame
        )
        create_home_section(categories_frame, word,
                            "Alternativas", 3, toggle_alternativas)
        create_home_section(categories_frame, word,
                            "Antónimos / Contraste", 5, toggle_contraste)
        bottom_spacer = ctk.CTkFrame(
            categories_frame,
            height=220,
            fg_color="transparent"
        )

        bottom_spacer.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew"
        )

    else:
        message.configure(
            text="Palabra no encontrada."
        )


def show_home(content):
    clear_content(content)

    content.grid_columnconfigure(0, weight=1)

    search_frame = paper_frame(content)

    search_frame.grid(
        row=0,
        column=0,
        padx=24,
        pady=(140, 20)
    )

    home_title = paper_label(
        search_frame,
        text="Word Bank",
        font=(SERIF, 34),
        text_color=INK
    )

    home_title.grid(
        row=0,
        column=0,
        pady=(0, 24)
    )

    entry = paper_entry(
        search_frame,
        placeholder_text="Introduce una palabra",
        width=700,
        height=44
    )

    entry.grid(
        row=1,
        column=0,
        pady=(0, 18)
    )

    message = paper_label(
        search_frame,
        text="Busca una palabra para iniciar."
    )

    categories_frame = paper_frame(content)

    categories_frame.grid(
        row=1,
        column=0,
        padx=40,
        pady=(20, 20),
        sticky="ew"
    )

    categories_frame.grid_columnconfigure(0, weight=1)

    button = paper_button(
        search_frame,
        text="Buscar",
        command=lambda: search_word(
            entry,
            message,
            categories_frame
        ),
        fg_color=ACCENT,
        hover_color="#3C3129",
        text_color="#F8F7F5"
    )

    button.grid(
        row=2,
        column=0,
        pady=(0, 18)
    )

    message.grid(
        row=3,
        column=0
    )


def save_new_word(entry, message):
    word = entry.get().strip()

    if not word or word == "0":
        message.configure(
            text="Introduce una palabra no vacía y distinta de 0.")
        return

    if buscar_clave_palabra(wordbank, word) in wordbank["palabras"]:
        message.configure(text="Esta palabra ya existe en el Word Bank.")
        return

    wordbank["palabras"][word] = {
        "sinonimos": [],
        "alternativas": [],
        "contraste": []
    }

    if guardar_wordbank(wordbank):
        message.configure(text=f'"{word}" fue guardada correctamente.')
        entry.delete(0, "end")
    else:
        del wordbank["palabras"][word]
        message.configure(
            text="No se pudo guardar la palabra. Intenta de nuevo.")


def show_add_word(form, message):
    clear_content(form)
    form.grid(row=4, column=0, padx=24, pady=8, sticky="ew")
    form.grid_rowconfigure(0, weight=0)
    form.grid_columnconfigure(0, weight=1)
    message.configure(text="Introduce la palabra que quieres añadir.")

    label = paper_label(form, text="Nueva palabra")
    label.grid(row=0, column=0, padx=8, pady=8, sticky="w")

    entry = paper_entry(form, placeholder_text="Nueva palabra")
    entry.grid(row=1, column=0, padx=8, pady=8, sticky="ew")

    save_button = paper_button(
        form,
        text="Guardar",
        command=lambda: save_new_word(entry, message),
        **PRIMARY_BUTTON_STYLE,
    )
    save_button.grid(row=2, column=0, padx=8, pady=8, sticky="w")
    entry.focus_set()


def save_synonyms(word, entry, message):
    synonyms = wordbank["palabras"][word]["sinonimos"]
    new_synonyms, duplicates = preparar_items(entry.get(), synonyms)

    if not new_synonyms:
        message.configure(text="No hay sinónimos nuevos para guardar.")
        return

    previous_synonyms = synonyms.copy()
    synonyms.extend(new_synonyms)

    if guardar_wordbank(wordbank):
        message.configure(text=mensaje_items_guardados(
            len(new_synonyms), duplicates))
        entry.delete(0, "end")
    else:
        synonyms[:] = previous_synonyms
        message.configure(
            text="No se pudieron guardar los sinónimos. Intenta de nuevo.")


def save_contrast(word, entry, message):
    contrasts = wordbank["palabras"][word]["contraste"]
    new_items, duplicates = preparar_items(entry.get(), contrasts)

    if not new_items:
        message.configure(
            text="No hay elementos de contraste nuevos para guardar.")
        return

    previous_items = contrasts.copy()
    contrasts.extend(new_items)

    if guardar_wordbank(wordbank):
        message.configure(text=mensaje_items_guardados(
            len(new_items), duplicates))
        entry.delete(0, "end")
    else:
        contrasts[:] = previous_items
        message.configure(
            text="No se pudo guardar el contraste. Intenta de nuevo.")


def show_contrast_form(word, form, message):
    label = paper_label(form, text="Antónimos / Contraste")
    label.grid(row=0, column=0, padx=8, pady=(16, 8), sticky="w")

    entry = paper_entry(
        form, placeholder_text="Separados por comas: ignorar, evitar verlo"
    )
    entry.grid(row=1, column=0, padx=8, pady=8, sticky="ew")

    button = paper_button(
        form, text="Guardar contraste",
        command=lambda: save_contrast(word, entry, message),
        **PRIMARY_BUTTON_STYLE,
    )

    button.grid(row=2, column=0, padx=8, pady=8, sticky="w")


def refresh_emotion_options(frame, checkboxes):
    clear_content(frame)
    checkboxes.clear()
    emotions = []
    for data in wordbank["palabras"].values():
        for alternative in data["alternativas"]:
            for emotion in alternative["emociones"]:
                emotion = emotion.strip().lower()
                if emotion and emotion not in emotions:
                    emotions.append(emotion)

    emotions.sort()
    for i, emotion in enumerate(emotions):
        checkbox = paper_checkbox(frame, text=emotion)
        checkbox.grid(row=i // 2, column=i % 2, padx=8, pady=4, sticky="w")
        checkboxes.append((emotion, checkbox))

    if not emotions:
        label = paper_label(
            frame, text="Puedes añadir emociones nuevas abajo.")
        label.grid(row=0, column=0, padx=8, pady=4, sticky="w")


def save_alternative(word, entry, custom_emotions, body_checkbox,
                     emotion_frame, checkboxes, message):
    text = entry.get().strip()
    if not text:
        message.configure(text="La alternativa no puede quedar vacía.")
        return

    if any(normalizar_comparacion(item["texto"]) == normalizar_comparacion(text)
           for item in wordbank["palabras"][word]["alternativas"]):
        message.configure(text="La alternativa ya existe.")
        return

    selected = [emotion for emotion, checkbox in checkboxes if checkbox.get()]
    emotions = []
    for emotion in selected + custom_emotions.get().split(","):
        emotion = emotion.strip().lower()
        if emotion and emotion not in emotions:
            emotions.append(emotion)

    alternative = {
        "texto": text,
        "emociones": emotions,
        "lenguaje_corporal": bool(body_checkbox.get()),
        "favorito": False
    }
    alternatives = wordbank["palabras"][word]["alternativas"]
    alternatives.append(alternative)

    if not guardar_wordbank(wordbank):
        alternatives.pop()
        message.configure(
            text="No se pudo guardar la alternativa. Intenta de nuevo.")
        return

    entry.delete(0, "end")
    custom_emotions.delete(0, "end")
    body_checkbox.deselect()
    refresh_emotion_options(emotion_frame, checkboxes)
    message.configure(text="Alternativa guardada correctamente.")
    entry.focus_set()


def show_alternative_form(word, form, message):
    label = paper_label(form, text="Alternativas")
    label.grid(row=0, column=0, padx=8, pady=(16, 8), sticky="w")

    entry = paper_entry(form, placeholder_text="Una alternativa a la vez")
    entry.grid(row=1, column=0, padx=8, pady=8, sticky="ew")

    label = paper_label(form, text="Emociones (puedes seleccionar varias)")
    label.grid(row=2, column=0, padx=8, pady=8, sticky="w")

    emotion_frame = paper_frame(form, fg_color="transparent")
    emotion_frame.grid(row=3, column=0, padx=8, pady=4, sticky="ew")
    checkboxes = []
    refresh_emotion_options(emotion_frame, checkboxes)

    custom_emotions = paper_entry(
        form, placeholder_text="Agregar emoción nueva: vergüenza, alivio"
    )
    custom_emotions.grid(row=4, column=0, padx=8, pady=8, sticky="ew")

    body_checkbox = paper_checkbox(form, text="Lenguaje corporal")
    body_checkbox.grid(row=5, column=0, padx=8, pady=8, sticky="w")

    button = paper_button(
        form,
        text="Guardar alternativa",
        command=lambda: save_alternative(
            word, entry, custom_emotions, body_checkbox,
            emotion_frame, checkboxes, message
        ),
        **PRIMARY_BUTTON_STYLE,
    )

    button.grid(row=6, column=0, padx=8, pady=8, sticky="w")


def show_word_edit_form(word_entry, form, message):
    word = word_entry.get().strip().lower()
    if not word:
        message.configure(text="Introduce una palabra.")
        return
    word = buscar_clave_palabra(wordbank, word)
    if word not in wordbank["palabras"]:
        message.configure(text="Esa palabra no existe en el wordbank.")
        return

    clear_content(form)
    message.configure(text="")
    form.grid_configure(sticky="ew")
    form.grid_rowconfigure(0, weight=0)

    workspace = paper_frame(form)
    workspace.grid(row=0, column=0, sticky="ew")
    heading = paper_label(
        workspace, text=f'Editando: "{word}"', font=(SERIF, 20), text_color=INK
    )
    heading.grid(row=0, column=0, columnspan=2, pady=(8, 20))

    text_sections = paper_frame(workspace)
    alternatives_section = paper_frame(workspace)
    text_sections.grid_columnconfigure(0, weight=1)
    alternatives_section.grid_columnconfigure(0, weight=1)

    workspace.grid_columnconfigure(0, weight=1)
    text_sections.grid(row=1, column=0, sticky="ew")
    alternatives_section.grid(row=2, column=0, pady=(24, 0), sticky="ew")

    form = text_sections

    label = paper_label(form, text="Sinónimos")
    label.grid(row=0, column=0, padx=8, pady=8, sticky="w")

    entry = paper_entry(
        form, placeholder_text="Separados por comas: andar, avanzar")
    entry.grid(row=1, column=0, padx=8, pady=8, sticky="ew")

    button = paper_button(
        form, text="Guardar sinónimos",
        command=lambda: save_synonyms(word, entry, message),
        **PRIMARY_BUTTON_STYLE,
    )

    button.grid(row=2, column=0, padx=8, pady=8, sticky="w")
    contrast = paper_frame(text_sections)
    contrast.grid(row=3, column=0, pady=(24, 0), sticky="ew")
    contrast.grid_columnconfigure(0, weight=1)
    show_contrast_form(word, contrast, message)
    show_alternative_form(word, alternatives_section, message)
    entry.focus_set()


def show_edit_existing_word(form, message):
    clear_content(form)
    form.grid(row=4, column=0, padx=24, pady=8, sticky="ew")
    form.grid_rowconfigure(0, weight=0)
    form.grid_columnconfigure(0, weight=1)
    message.configure(text="Introduce una palabra existente.")

    label = paper_label(form, text="Palabra que quieres editar")
    label.grid(row=0, column=0, padx=8, pady=8, sticky="w")

    entry = paper_entry(form, placeholder_text="Palabra existente")
    entry.grid(row=1, column=0, padx=8, pady=8, sticky="ew")

    button = paper_button(
        form, text="Editar",
        command=lambda: show_word_edit_form(entry, form, message),
        **PRIMARY_BUTTON_STYLE,
    )
    button.grid(row=2, column=0, padx=8, pady=8, sticky="w")
    entry.focus_set()


def show_edit_wordbank(content):
    clear_content(content)

    title = paper_label(
        content,
        text="Editar Wordbank",
        font=(SERIF, 38),
        text_color=INK
    )

    title.grid(
        row=0,
        column=0,
        padx=24,
        pady=(24, 16),
        sticky=""
    )

    divider = ctk.CTkFrame(
        content,
        height=1,
        fg_color=BORDER,
        corner_radius=0
    )

    divider.grid(
        row=1,
        column=0,
        padx=180,
        pady=(0, 28),
        sticky="ew"
    )

    form = paper_frame(
        content,
        fg_color="transparent"
    )

    actions = paper_frame(content)

    actions.grid(
        row=2,
        column=0,
        padx=24,
        pady=(0, 16)
    )

    message = paper_label(
        content,
        text="Selecciona una acción de edición."
    )

    message.grid(
        row=3,
        column=0,
        padx=24,
        pady=8,
        sticky=""
    )

    add_button = paper_button(
        actions,
        text="Añadir palabra",
        command=lambda: show_add_word(form, message),
        **PRIMARY_BUTTON_STYLE,
    )

    add_button.grid(
        row=0,
        column=0,
        padx=(0, 8),
        pady=0,
        sticky=""
    )

    edit_button = paper_button(
        actions,
        text="Editar palabra",
        command=lambda: show_edit_existing_word(form, message),
        **PRIMARY_BUTTON_STYLE,
    )

    edit_button.grid(
        row=0,
        column=1,
        padx=(8, 0),
        pady=0,
        sticky=""
    )


def search_favorites(entry, message, results):
    word = entry.get().strip().lower()
    clear_content(results)

    if not word:
        message.configure(text="Introduce una palabra.")
        return
    word = buscar_clave_palabra(wordbank, word)
    if word not in wordbank["palabras"]:
        message.configure(text="Palabra no encontrada.")
        return

    display_favorites(word, message, results)


def remove_favorite(word, original_index, message, results):
    item = wordbank["palabras"][word]["alternativas"][original_index]
    previous = item["favorito"]
    item["favorito"] = False

    if not guardar_wordbank(wordbank):
        item["favorito"] = previous
        message.configure(
            text="No se pudo quitar el favorito. Intenta de nuevo.")
        return

    display_favorites(word, message, results)


def display_favorites(word, message, results):
    clear_content(results)
    message.configure(text="")
    title = paper_label(results, text=word.upper(),
                        font=(SERIF, 44), text_color=INK)
    title.grid(row=0, column=0, columnspan=2,
               padx=8, pady=(26, 28), sticky="ew")

    label = paper_label(results, text="Alternativas favoritas",
                        font=(SERIF, 23), text_color=INK)
    label.grid(row=1, column=0, padx=8, pady=(16, 4), sticky="w")
    favorites = [
        (index, item)
        for index, item in enumerate(wordbank["palabras"][word]["alternativas"])
        if isinstance(item, dict) and item.get("favorito") is True
    ]
    if not favorites:
        paper_label(results, text="No hay alternativas favoritas para esta palabra.").grid(
            row=2, column=0, padx=8, pady=5, sticky="w"
        )

    for number, (original_index, item) in enumerate(favorites, start=1):
        text = item["texto"]
        label = paper_label(
            results, text=f"{number}. {text[:1].upper() + text[1:]}"
        )
        label.grid(row=number + 1, column=0, padx=8, pady=5, sticky="w")
        button = paper_button(
            results, text="♥", width=32,
            command=lambda index=original_index: remove_favorite(
                word, index, message, results
            )
        )
        button.grid(row=number + 1, column=1, padx=8, pady=5, sticky="e")


def favorite_words():
    return sorted(
        [word for word, data in wordbank["palabras"].items()
         if any(isinstance(item, dict) and item.get("favorito") is True
                for item in data["alternativas"])],
        key=normalizar_comparacion
    )


def display_favorite_words(results, open_word):
    clear_content(results)
    words = favorite_words()
    heading = paper_label(
        results, text="Palabras con favoritos", font=(SERIF, 23), text_color=INK)
    heading.grid(row=0, column=0, padx=8, pady=(16, 12), sticky="w")
    if not words:
        paper_label(results, text="Todavía no tienes favoritos guardados.").grid(
            row=1, column=0, padx=8, pady=8, sticky="w"
        )
        return

    flow = paper_frame(results, height=1)
    flow.grid(row=1, column=0, padx=8, pady=4, sticky="ew")
    font = ctk.CTkFont(family=SERIF, size=18)
    last_width = None

    def arrange(event=None):
        nonlocal last_width
        width = flow.winfo_width()
        if width <= 1:
            width = max(100, results.winfo_width() - 16)
        if width == last_width:
            return
        last_width = width
        available = width / flow._get_widget_scaling()
        clear_content(flow)
        row = None
        used = 0
        for word in words:
            needed = min(available, font.measure(word) + 24)
            if row is None or used + needed > available:
                row = paper_frame(flow, height=1)
                row.pack(fill="x", pady=8)
                used = 0
            item = paper_frame(row, height=1)
            item.pack(side="left", padx=(0, 24), anchor="n")
            label = paper_label(item, text=word, font=(SERIF, 18), text_color=MUTED,
                                cursor="hand2", wraplength=max(1, available - 24))
            label.grid(row=0, column=0, sticky="w")
            label.bind("<Button-1>", lambda event, key=word: open_word(key))
            line = ctk.CTkFrame(item, width=1, height=1, fg_color=BORDER,
                                corner_radius=0, cursor="hand2")
            line.grid(row=1, column=0, sticky="ew")
            line.bind("<Button-1>", lambda event, key=word: open_word(key))
            used += needed

    flow.bind("<Configure>", arrange)
    arrange()


def show_favorites(content):
    clear_content(content)

    title = paper_label(content, text="Favoritos",
                        font=(SERIF, 38), text_color=INK)
    title.grid(row=0, column=0, padx=24, pady=(24, 16), sticky="")

    entry = paper_entry(content, placeholder_text="Introduce una palabra")
    entry.grid(row=1, column=0, padx=24, pady=8, sticky="ew")

    message = paper_label(
        content, text="Busca una palabra para ver sus favoritos.")
    message.grid(row=3, column=0, padx=24, pady=8, sticky="")

    results = paper_frame(content)
    results.grid(row=4, column=0, padx=24, pady=(8, 16), sticky="nsew")
    results.grid_columnconfigure(0, weight=1)
    actions = paper_frame(content)
    actions.grid(row=2, column=0, padx=24, pady=8)

    def search():
        back.configure(state="normal")
        search_favorites(entry, message, results)

    def open_word(word):
        entry.delete(0, "end")
        entry.insert(0, word)
        search()

    def show_words():
        entry.delete(0, "end")
        message.configure(text="Selecciona una palabra o busca sus favoritos.")
        back.configure(state="disabled")
        # Recompute rather than cache: the last favorite may have been removed.
        display_favorite_words(results, open_word)

    button = paper_button(
        actions,
        text="Buscar",
        command=search,
        **PRIMARY_BUTTON_STYLE,
    )

    button.grid(row=0, column=0, padx=4)

    back = paper_button(actions, text="← Volver", command=show_words,
                        fg_color="transparent", border_width=0, text_color=MUTED)
    back.grid(row=0, column=1, padx=4)
    show_words()


def main():
    ctk.set_appearance_mode("light")
    window = ctk.CTk()
    window.title("Word Bank")
    window.configure(fg_color=PAPER)
    window.geometry("920x760")
    window.minsize(620, 480)
    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(2, weight=1)

    navigation = paper_frame(window)
    navigation.grid(row=1, column=0, pady=(36, 18))

    page = paper_frame(window)
    page.grid(row=2, column=0, sticky="nsew", pady=(0, 16))
    content = paper_scroll(page)
    content.grid_columnconfigure(0, weight=1)

    page.grid_columnconfigure(0, weight=1)
    page.grid_rowconfigure(0, weight=1)
    content.grid(row=0, column=0, sticky="nsew")

    def scroll_main_page(event):
        target = event.widget
        if target == window:
            target = window.winfo_containing(event.x_root, event.y_root)
        while target is not None and target != content._parent_canvas:
            if isinstance(target, (ctk.CTkTextbox, ctk.CTkScrollbar)):
                return
            target = getattr(target, "master", None)
        if target is None:
            return
        delta = event.delta
        if window.tk.call("tk", "windowingsystem") != "aqua":
            delta = int(delta / 120) if abs(delta) >= 120 else delta
        if delta:
            content._parent_canvas.yview_scroll(-int(delta), "units")
        return "break"

    window.bind("<MouseWheel>", scroll_main_page, add="+")

    tabs = []

    def select_page(index, show_page):
        for i, button in enumerate(tabs):
            button.configure(
                fg_color=SURFACE if i == index else "transparent",
                border_color=BORDER if i == index else PAPER,
                text_color=INK if i == index else MUTED,
                font=(SANS, 14, "bold" if i == index else "normal")
            )
        show_page(content)

    for i, (text, show_page) in enumerate([
        ("Inicio", show_home),
        ("Editar Wordbank", show_edit_wordbank),
        ("Favoritos", show_favorites)
    ]):
        button = paper_button(
            navigation, text=text, width=160, height=38,
            fg_color="transparent", hover_color=SURFACE, text_color=MUTED,
            border_width=1, border_color=PAPER,
            command=lambda index=i, show=show_page: select_page(index, show)
        )
        button.grid(row=0, column=i, padx=3)
        tabs.append(button)

    select_page(0, show_home)
    window.mainloop()


if __name__ == "__main__":
    main()
