import logging
import collections
from tkinter import filedialog, messagebox, Canvas, PhotoImage, Menu, Toplevel, Text
from tkinter import ttk
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageGrab
from gui.edit_tab import EditTab
from gui.filter_tab import FilterTab
from gui.draw_tab import DrawTab
from utilities.tooltip import Tooltip
from utilities.image_processing import apply_adjustments
import os

class PhotoEditor:
    def __init__(self, root):
        logging.info("Инициализация PhotoEditor")
        self.root = root
        self.root.title("Фоторедактор")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        self.root.configure(bg="#2E3440")

        # Установка иконки приложения
        icon_path = os.path.join(os.path.dirname(__file__), 'image', 'frame.ico')

        # Настройка стилей для виджетов
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#2E3440")
        self.style.configure("TLabel", background="#2E3440", foreground="#D8DEE9", font=("Helvetica", 12))
        self.style.configure("TButton", background="#5E81AC", foreground="#ECEFF4", font=("Helvetica", 12, "bold"), focuscolor='none')
        self.style.configure("TScale", background="#2E3440", troughcolor="#4C566A", sliderrelief="flat", sliderlength=15)
        self.style.map("TButton", background=[('active', '#81A1C1')])

        # Инициализация истории и стека для отмены/повтора действий
        self.history = collections.deque(maxlen=20)
        self.redo_stack = collections.deque(maxlen=20)

        # Создание фрейма для кнопок
        self.button_frame = ttk.Frame(root)
        self.button_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Кнопка загрузки изображения
        self.load_button = ttk.Button(self.button_frame, text="Загрузить изображение", command=self.load_image_from_dialog)
        self.load_button.pack(pady=10)
        self.add_tooltip(self.load_button, "Загрузить изображение из файла")

        # Кнопка сохранения изображения
        self.save_button = ttk.Button(self.button_frame, text="Сохранить изображение", command=self.save_image_to_dialog)
        self.save_button.pack(pady=10)
        self.add_tooltip(self.save_button, "Сохранить текущее изображение в файл")

        # Загрузка изображений для кнопок отмены и повтора с проверкой успешности
        self.undo_photo = self.load_image_safe('image/undo.png', (30, 30))
        if self.undo_photo is None:
            logging.error("Не удалось загрузить изображение для кнопки отмены")
            self.undo_button = ttk.Button(self.button_frame, text="Отмена", command=self.undo, style="TButton")
        else:
            self.undo_button = ttk.Button(self.button_frame, image=self.undo_photo, command=self.undo, style="TButton")
        self.undo_button.pack(pady=10)
        self.add_tooltip(self.undo_button, "Отменить последнее действие")

        self.redo_photo = self.load_image_safe('image/redo.png', (30, 30))
        if self.redo_photo is None:
            logging.error("Не удалось загрузить изображение для кнопки повтора")
            self.redo_button = ttk.Button(self.button_frame, text="Повтор", command=self.redo, style="TButton")
        else:
            self.redo_button = ttk.Button(self.button_frame, image=self.redo_photo, command=self.redo, style="TButton")
        self.redo_button.pack(pady=10)
        self.add_tooltip(self.redo_button, "Повторить последнее действие")

        # Создание вкладок для инструментов редактирования и фильтров
        self.notebook = ttk.Notebook(self.button_frame)
        self.notebook.pack(pady=10)

        self.edit_tab = EditTab(self.notebook, self)
        self.notebook.add(self.edit_tab.frame, text="Редактирование")

        self.filter_tab = FilterTab(self.notebook, self)
        self.notebook.add(self.filter_tab.frame, text="Фильтры")

        # Создание холста для отображения изображения
        self.image_canvas = Canvas(root, bg="#3B4252", highlightbackground="#2E3440", highlightthickness=1)
        self.image_canvas.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.image = None
        self.image_path = None
        self.display_image = None
        self.original_image = None

        self.draw_tab = DrawTab(self.notebook, self)

        # Переменные для выделения области
        self.selection_top_x = 0
        self.selection_top_y = 0
        self.selection_bottom_x = 0
        self.selection_bottom_y = 0
        self.selection_rect = None

        # Обработка изменения размера холста
        self.image_canvas.bind("<Configure>", self.on_canvas_resize)
        self.add_menu()

    def add_tooltip(self, widget, text):
        #Функция для добавления подсказок к виджетам
        tooltip = Tooltip(widget, text)
        widget.bind("<Enter>", lambda event, t=tooltip: t.showtip())
        widget.bind("<Leave>", lambda event, t=tooltip: t.hidetip())

    def load_image_safe(self, path, size):
        """
        Безопасная загрузка изображения с изменением размера.
        
        Args:
           path (str): Путь к изображению.
           size (tuple): Размер изображения (ширина, высота).
        
        Returns:
            ImageTk.PhotoImage: Изображение для использования в Tkinter или None, если не удалось загрузить.
        """
        try:
            image = Image.open(path)
            image = image.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            logging.error(f"Ошибка загрузки изображения {path}: {e}")
            return None

    def load_image_from_dialog(self):
        #Загрузка изображения из диалогового окна
        file_path = filedialog.askopenfilename()
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        #Загрузка изображения и обновление состояния приложения
        try:
            logging.info(f"Загрузка изображения: {file_path}")
            self.image = Image.open(file_path)
            self.original_image = self.image.copy()
            self.image_path = file_path
            self.history.clear()
            self.redo_stack.clear()
            self.reset_sliders()
            self.save_history()
            self.update_canvas_size()
            self.update_display_image()
        except Exception as e:
            logging.error(f"Ошибка при загрузке изображения {file_path}: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")

    def save_image_to_dialog(self):
        #Сохранение изображения через диалоговое окно
        if self.image:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
            if save_path:
                self.save_image(save_path)

    def save_image(self, save_path):
        #Сохранение изображения по указанному пути
        try:
            if self.image:
                logging.info(f"Сохранение изображения: {save_path}")
                final_image = self.draw_tab.get_final_image()
                final_image.save(save_path)
            else:
                logging.error("Нет изображения для сохранения")
                messagebox.showerror("Ошибка", "Нет изображения для сохранения")
        except Exception as e:
            logging.error(f"Ошибка при сохранении изображения {save_path}: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {e}")

    def capture_canvas(self):
        #Захват текущего содержимого холста
        x = self.root.winfo_rootx() + self.image_canvas.winfo_x()
        y = self.root.winfo_rooty() + self.image_canvas.winfo_y()
        x1 = x + self.image_canvas.winfo_width()
        y1 = y + self.image_canvas.winfo_height()
        return ImageGrab.grab().crop((x, y, x1, y1))

    def save_history(self):
        #Сохранение текущего состояния изображения в историю
        if self.image:
            logging.info("Сохранение текущего состояния изображения в историю")
            self.history.append((self.image.copy(), self.original_image.copy(), self.get_slider_values(), list(self.draw_tab.drawn_items), list(self.draw_tab.text_items)))
            self.redo_stack.clear()
            logging.debug(f"История сохранена в PhotoEditor: {len(self.history)} элементов")

    def undo(self):
        #Отмена последнего действия
        if len(self.history) > 1:
            logging.info("Отмена последнего действия в PhotoEditor")
            self.redo_stack.append(self.history.pop())
            self.image, self.original_image, slider_values, drawn_state, text_state = self.history[-1]
            self.update_display_image()
            self.set_slider_values(slider_values)
            self.draw_tab.drawn_items = drawn_state
            self.draw_tab.text_items = text_state
            self.draw_tab.redraw_items()
            logging.debug(f"История после отмены: {len(self.history)} элементов")
        else:
            logging.warning("Нет действий для отмены в PhotoEditor")

    def redo(self):
        #Повтор последнего отмененного действия
        if self.redo_stack:
            logging.info("Повтор последнего действия в PhotoEditor")
            self.history.append(self.redo_stack.pop())
            self.image, self.original_image, slider_values, drawn_state, text_state = self.history[-1]
            self.update_display_image()
            self.set_slider_values(slider_values)
            self.draw_tab.drawn_items = drawn_state
            self.draw_tab.text_items = text_state
            self.draw_tab.redraw_items()
            logging.debug(f"История после повтора: {len(self.history)} элементов")
        else:
            logging.warning("Нет действий для повтора в PhotoEditor")

    def update_canvas_size(self):
        #Обновление размера холста в зависимости от изображения
        if self.image:
            self.image_canvas.config(scrollregion=(0, 0, self.image.width, self.image.height))

    def update_display_image(self, region=None):
        try:
            if region:
                x0, y0, x1, y1 = region
                self.image_canvas.delete("region")
                resized_image = self.image.crop((x0, y0, x1, y1))
                self.display_image = ImageTk.PhotoImage(resized_image)
                self.image_canvas.create_image(x0, y0, anchor="nw", image=self.display_image, tags="region")
            else:
                self.image_canvas.delete("all")
                if self.image:
                    canvas_width = self.image_canvas.winfo_width()
                    canvas_height = self.image_canvas.winfo_height()
                    image_width, image_height = self.image.size

                    scale = min(canvas_width / image_width, canvas_height / image_height, 1.0)
                    new_width = int(image_width * scale)
                    new_height = int(image_height * scale)

                    resized_image = self.image.resize((new_width, new_height), Image.LANCZOS)
                    self.display_image = ImageTk.PhotoImage(resized_image)
                    self.image_canvas.create_image((canvas_width // 2, canvas_height // 2), anchor="center", image=self.display_image)
                    self.image_canvas.image = self.display_image
                    self.draw_tab.redraw_items()
        except Exception as e:
            logging.error(f"Ошибка при обновлении изображения: {e}")

    def reset_sliders(self):
        #Сброс значений ползунков к исходным
        self.edit_tab.reset_sliders()
        self.filter_tab.reset_sliders()

    def get_slider_values(self):
        #Получение текущих значений ползунков
        return {
            "brightness": self.filter_tab.brightness_scale.get(),
            "contrast": self.filter_tab.contrast_scale.get(),
            "saturation": self.filter_tab.saturation_scale.get(),
            "width": self.edit_tab.width_scale.get(),
            "height": self.edit_tab.height_scale.get(),
            "blur": self.filter_tab.blur_scale.get()
        }

    def set_slider_values(self, values):
        #Установка значений ползунков
        self.filter_tab.brightness_scale.set(values["brightness"])
        self.filter_tab.contrast_scale.set(values["contrast"])
        self.filter_tab.saturation_scale.set(values["saturation"])
        self.edit_tab.width_scale.set(values["width"])
        self.edit_tab.height_scale.set(values["height"])
        self.filter_tab.blur_scale.set(values["blur"])
        self.filter_tab.brightness_value_label.config(text=f"{values['brightness']:.1f}")
        self.filter_tab.contrast_value_label.config(text=f"{values['contrast']:.1f}")
        self.filter_tab.saturation_value_label.config(text=f"{values['saturation']:.1f}")
        self.edit_tab.width_value_label.config(text=str(int(values["width"])))
        self.edit_tab.height_value_label.config(text=str(int(values["height"])))
        self.filter_tab.blur_value_label.config(text=str(int(values["blur"])))

    def apply_adjustments(self):
        #Применение изменений к изображению
        if self.original_image:
            logging.info("Применение настроек к изображению")
            new_width = max(100, int(self.edit_tab.width_scale.get()))
            new_height = max(100, int(self.edit_tab.height_scale.get()))
            brightness = self.filter_tab.brightness_scale.get()
            contrast = self.filter_tab.contrast_scale.get()
            saturation = self.filter_tab.saturation_scale.get()
            blur_radius = self.filter_tab.blur_scale.get()

            self.image = apply_adjustments(self.original_image, new_width, new_height, brightness, contrast, saturation, blur_radius)
            self.update_display_image()
        else:
            logging.error("Изображение не загружено")
            messagebox.showerror("Ошибка", "Изображение не загружено")

    def start_area_selection(self):
        #Начало выделения области для обрезки
        self.image_canvas.bind("<Button-1>", self.get_selection_start_pos)
        self.image_canvas.bind("<B1-Motion>", self.update_selection)
        self.image_canvas.bind("<ButtonRelease-1>", self.finalize_selection)

    def get_selection_start_pos(self, event):
        #Получение начальной позиции выделения
        self.selection_top_x, self.selection_top_y = event.x, event.y
        self.selection_rect = self.image_canvas.create_rectangle(self.selection_top_x, self.selection_top_y, self.selection_top_x, self.selection_top_y, dash=(2, 2), outline="white")

    def update_selection(self, event):
        #Обновление выделяемой области
        self.selection_bottom_x, self.selection_bottom_y = event.x, event.y
        self.image_canvas.coords(self.selection_rect, self.selection_top_x, self.selection_top_y, self.selection_bottom_x, self.selection_bottom_y)

    def finalize_selection(self, event):
        #Завершение выделения области
        self.image_canvas.unbind("<Button-1>")
        self.image_canvas.unbind("<B1-Motion>")
        self.image_canvas.unbind("<ButtonRelease-1>")
        self.crop_image()

    def crop_image(self):
        #Обрезка изображения по выделенной области
        if self.image:
            cropped_image = self.image.crop((self.selection_top_x, self.selection_top_y, self.selection_bottom_x, self.selection_bottom_y))
            self.image = cropped_image
            self.update_canvas_size()
            self.update_display_image()
            self.save_history()

    def on_canvas_resize(self, event):
        #Обработка изменения размера холста
        self.update_display_image()

    def show_documentation(self):
        #Отображение окна документации
        doc_window = Toplevel(self.root)
        doc_window.title("Документация")
        doc_window.geometry("600x800")
        doc_window.configure(bg="#2E3440")

        text_widget = Text(doc_window, wrap="word", bg="#3B4252", fg="#D8DEE9", font=("Helvetica", 12))
        text_widget.pack(expand=1, fill="both")

        documentation_content = """
        Введение
        Добро пожаловать в фоторедактор! Эта программа позволяет 
        редактировать изображения, применяя различные фильтры и изменения. Вы 
        можете изменять размер, обрезать, поворачивать изображения, 
        регулировать 
        яркость, контрастность, насыщенность и размытие, а также рисовать и 
        добавлять текст на изображениях.

        Основные функции
        Загрузка изображения
        1. Нажмите кнопку "Загрузить изображение".
        2. Выберите изображение в диалоговом окне.

        Сохранение изображения
        1. Нажмите кнопку "Сохранить изображение".
        2. Выберите место и формат для сохранения.

        Изменение размеров
        1. Используйте ползунки "Ширина" и "Высота" во вкладке "Редактирование" 
        для изменения размеров изображения.
        2. Для ручного ввода размеров нажмите "Ввести размеры вручную".

        Поворот изображения
        1. Нажмите кнопку "Повернуть" во вкладке "Редактирование".
        2. Введите угол поворота и нажмите "Применить".

        Обрезка изображения
        1. Нажмите кнопку "Обрезать" во вкладке "Редактирование".
        2. Выделите область для обрезки и завершите действие.

        Регулировка яркости, контрастности, насыщенности и размытия
        1. Перейдите во вкладку "Фильтры".
        2. Используйте соответствующие ползунки для регулировки.

        Рисование и добавление текста
        1. Перейдите во вкладку "Рисование".
        2. Используйте кнопки для выбора цвета, добавления текста и начала 
        рисования.

        Дополнительные функции
        Отмена и повтор действий
        1. Нажмите кнопку "Отмена" для отмены последнего действия.
        2. Нажмите кнопку "Повтор" для повтора последнего действия.

        Подсказки и советы
        - Наведите курсор на кнопки и ползунки, чтобы увидеть подсказки по их 
        использованию.
        - Используйте вкладки для быстрого доступа к различным инструментам 
        редактирования.


        """

        text_widget.insert("1.0", documentation_content)
        text_widget.config(state="disabled")

    def add_menu(self):
        #Добавление меню в приложение
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Загрузить изображение", command=self.load_image_from_dialog)
        file_menu.add_command(label="Сохранить изображение", command=self.save_image_to_dialog)
        menu_bar.add_cascade(label="Файл", menu=file_menu)

        edit_menu = Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Отмена", command=self.undo)
        edit_menu.add_command(label="Повтор", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Начать выделение", command=self.start_area_selection)
        menu_bar.add_cascade(label="Правка", menu=edit_menu)

        in_development_menu = Menu(menu_bar, tearoff=0)
        in_development_menu.add_command(label="Выбрать цвет", command=self.draw_tab.choose_color)
        in_development_menu.add_command(label="Добавить текст", command=self.draw_tab.add_text)
        in_development_menu.add_command(label="Рисовать", command=self.draw_tab.toggle_drawing)
        menu_bar.add_cascade(label="В разработке", menu=in_development_menu)

        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Документация", command=self.show_documentation)
        menu_bar.add_cascade(label="Справка", menu=help_menu)
