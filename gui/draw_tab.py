import logging
import collections
from tkinter import ttk, colorchooser, simpledialog, font
from PIL import Image, ImageDraw, ImageFont, ImageOps

class DrawTab:
    def __init__(self, notebook, editor):
        logging.info("Инициализация DrawTab")
        self.editor = editor
        self.frame = ttk.Frame(notebook, style="TFrame")

        self.drawing = False
        self.color = "#000000"
        self.brush_size = 3
        self.start_x = None
        self.start_y = None
        self.drawn_items = []
        self.text_items = []
        self.selected_text = None
        self.selected_text_item = None
        self.dragging = False

        self.history = collections.deque(maxlen=20)
        self.redo_stack = collections.deque(maxlen=20)

        self.setup_ui()

    def setup_ui(self):
        logging.info("Настройка UI для DrawTab")
        # Кнопка для выбора цвета кисти
        self.color_button = ttk.Button(self.frame, text="Выбрать цвет", command=self.choose_color)
        self.color_button.pack(pady=10)
        self.editor.add_tooltip(self.color_button, "Выбрать цвет кисти")

        # Ползунок для выбора размера кисти
        self.brush_size_label = ttk.Label(self.frame, text="Размер кисти")
        self.brush_size_label.pack(pady=5)
        self.brush_size_scale = ttk.Scale(self.frame, from_=1, to=10, orient="horizontal", command=self.update_brush_size)
        self.brush_size_scale.set(self.brush_size)
        self.brush_size_scale.pack(pady=5)
        self.editor.add_tooltip(self.brush_size_scale, "Изменить размер кисти")

        # Кнопка для добавления текста
        self.text_button = ttk.Button(self.frame, text="Добавить текст", command=self.add_text)
        self.text_button.pack(pady=10)
        self.editor.add_tooltip(self.text_button, "Добавить текст на изображение")

        # Кнопка для переключения режима рисования
        self.draw_button = ttk.Button(self.frame, text="Рисовать", command=self.toggle_drawing)
        self.draw_button.pack(pady=10)
        self.editor.add_tooltip(self.draw_button, "Рисовать на изображении")

        # Комбобокс для выбора шрифта
        self.font_label = ttk.Label(self.frame, text="Шрифт")
        self.font_label.pack(pady=5)
        self.font_combobox = ttk.Combobox(self.frame, values=font.families())
        self.font_combobox.pack(pady=5)
        self.font_combobox.set("Arial")
        self.editor.add_tooltip(self.font_combobox, "Выбрать шрифт для текста")

        # Ползунок для выбора размера шрифта
        self.font_size_label = ttk.Label(self.frame, text="Размер шрифта")
        self.font_size_label.pack(pady=5)
        self.font_size_scale = ttk.Scale(self.frame, from_=10, to=100, orient="horizontal")
        self.font_size_scale.set(20)
        self.font_size_scale.pack(pady=5)
        self.editor.add_tooltip(self.font_size_scale, "Изменить размер шрифта")

    def choose_color(self):
        # Выбор цвета кисти
        self.color = colorchooser.askcolor()[1]
        logging.info(f"Выбранный цвет: {self.color}")

    def update_brush_size(self, event):
        # Обновление размера кисти
        self.brush_size = int(self.brush_size_scale.get())
        logging.info(f"Обновленный размер кисти: {self.brush_size}")

    def toggle_drawing(self):
        # Переключение режима рисования
        self.drawing = not self.drawing
        logging.info(f"Режим рисования: {self.drawing}")
        if self.drawing:
            self.editor.image_canvas.bind("<B1-Motion>", self.paint)
            self.editor.image_canvas.bind("<ButtonRelease-1>", self.reset)
        else:
            self.editor.image_canvas.unbind("<B1-Motion>")
            self.editor.image_canvas.unbind("<ButtonRelease-1>")

    def paint(self, event):
        # Рисование на изображении
        if self.start_x and self.start_y:
            x1, y1 = (self.start_x, self.start_y)
            x2, y2 = (event.x, event.y)
            self.draw_line(x1, y1, x2, y2)
            self.start_x, self.start_y = x2, y2

            self.drawn_items.append((x1, y1, x2, y2, self.color, self.brush_size))
            logging.debug(f"Рисование линии: ({x1}, {y1}) -> ({x2}, {y2}), цвет: {self.color}, размер кисти: {self.brush_size}")
        else:
            self.start_x, self.start_y = event.x, event.y

    def reset(self, event):
        # Сброс координат рисования
        self.start_x, self.start_y = None, None
        logging.debug("Сброс координат рисования")
        self.save_history()

    def draw_line(self, x1, y1, x2, y2):
        # Отрисовка линии на изображении
        draw = ImageDraw.Draw(self.editor.image)
        draw.line((x1, y1, x2, y2), fill=self.color, width=self.brush_size)
        self.editor.update_display_image()

    def add_text(self):
        # Добавление текста на изображение
        text = simpledialog.askstring("Добавить текст", "Введите текст:")
        if text:
            font_family = self.font_combobox.get()
            font_size = int(self.font_size_scale.get())
            x, y = 100, 100

            self.text_items.append({"id": None, "text": text, "font_family": font_family, "font_size": font_size, "x": x, "y": y, "color": self.color})
            self.update_text_on_canvas(self.text_items[-1])
            self.save_history()

    def draw_text(self, text, font_family, font_size, x, y, color):
        # Отрисовка текста на изображении
        draw = ImageDraw.Draw(self.editor.image)
        try:
            font_path = f"C:/Windows/Fonts/{font_family}.ttf"
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
        draw.text((x, y), text, font=font, fill=color)
        self.editor.update_display_image()

    def update_text_on_canvas(self, text_item):
        # Обновление текста на холсте
        text_item["id"] = self.editor.image_canvas.create_text(
            text_item["x"], text_item["y"],
            text=text_item["text"], font=(text_item["font_family"], text_item["font_size"]),
            fill=text_item["color"], anchor="nw"
        )
        self.bind_text_events(text_item["id"])

    def bind_text_events(self, text_id):
        # Привязка событий к тексту на холсте
        self.editor.image_canvas.tag_bind(text_id, "<ButtonPress-1>", self.select_text)
        self.editor.image_canvas.tag_bind(text_id, "<B1-Motion>", self.drag_text)
        self.editor.image_canvas.tag_bind(text_id, "<ButtonRelease-1>", self.release_text)

    def select_text(self, event):
        # Выбор текстового элемента
        text_id = self.editor.image_canvas.find_closest(event.x, event.y)[0]
        logging.info(f"Выбран текстовый элемент с ID: {text_id}")
        self.selected_text = text_id
        self.selected_text_item = next((item for item in self.text_items if item["id"] == text_id), None)
        if self.selected_text_item:
            self.dragging = True
            logging.debug(f"Выбранный текстовый элемент: {self.selected_text_item}")
        else:
            logging.error(f"Текстовый элемент с ID {text_id} не найден")

    def drag_text(self, event):
        # Перемещение текстового элемента
        if self.dragging and self.selected_text:
            self.editor.image_canvas.coords(self.selected_text, event.x, event.y)
            self.selected_text_item["x"] = event.x
            self.selected_text_item["y"] = event.y
            logging.debug(f"Перемещение текста с ID {self.selected_text}: ({event.x}, {event.y})")

    def release_text(self, event):
        # Завершение перемещения текстового элемента
        self.dragging = False
        self.selected_text = None
        logging.debug("Завершение перемещения текста")
        self.save_history()

    def redraw_items(self):
        # Перерисовка элементов на холсте
        logging.info("Перерисовка элементов на Canvas")
        self.editor.image_canvas.delete("all")
        if self.editor.display_image:
            self.editor.image_canvas.create_image(0, 0, anchor="nw", image=self.editor.display_image)
        for item in self.drawn_items:
            x1, y1, x2, y2, color, brush_size = item
            logging.debug(f"Перерисовка линии: ({x1}, {y1}) -> ({x2}, {y2}), цвет: {color}, размер кисти: {brush_size}")
            self.editor.image_canvas.create_line(x1, y1, x2, y2, fill=color, width=brush_size, capstyle="round", smooth=True)
        for text_item in self.text_items:
            logging.debug(f"Перерисовка текста с ID {text_item['id']}: '{text_item['text']}', координаты: ({text_item['x']}, {text_item['y']})")
            self.update_text_on_canvas(text_item)

    def get_final_image(self):
        # Получение финального изображения с нарисованными элементами и текстом
        logging.info("Получение финального изображения")
        final_image = self.editor.image.copy()
        draw = ImageDraw.Draw(final_image)

        for item in self.drawn_items:
            x1, y1, x2, y2, color, brush_size = item
            draw.line((x1, y1, x2, y2), fill=color, width=brush_size)

        for text_item in self.text_items:
            try:
                font_path = f"C:/Windows/Fonts/{text_item['font_family']}.ttf"
                font = ImageFont.truetype(font_path, text_item["font_size"])
            except IOError:
                font = ImageFont.load_default()
            draw.text((text_item["x"], text_item["y"]), text_item["text"], fill=text_item["color"], font=font)

        return final_image

    def save_history(self):
        # Сохранение текущего состояния всех элементов в историю
        self.history.append((list(self.drawn_items), list(self.text_items)))
        self.redo_stack.clear()
        logging.debug(f"История сохранена. Текущая история: {self.history}")

    def undo(self):
        # Отмена последнего действия
        if len(self.history) > 0:
            self.redo_stack.append((list(self.drawn_items), list(self.text_items)))
            self.drawn_items, self.text_items = self.history.pop()
            self.redraw_items()
            logging.debug(f"Отмена действия. Текущая история: {self.history}")

    def redo(self):
        # Повтор последнего отмененного действия
        if len(self.redo_stack) > 0:
            self.history.append((list(self.drawn_items), list(self.text_items)))
            self.drawn_items, self.text_items = self.redo_stack.pop()
            self.redraw_items()
            logging.debug(f"Повтор действия. Текущая история: {self.history}")
