import logging
from tkinter import Entry, messagebox
from tkinter import ttk

class EditTab:
    def __init__(self, notebook, editor):
        logging.info("Инициализация EditTab")
        self.editor = editor
        self.frame = ttk.Frame(notebook, style="TFrame")

        # Фрейм и элементы управления для ширины
        self.width_frame = ttk.Frame(self.frame)
        self.width_frame.pack(pady=10)
        self.width_label = ttk.Label(self.width_frame, text="Ширина")
        self.width_label.pack(side="left")
        self.width_value_label = ttk.Label(self.width_frame, text="100")
        self.width_value_label.pack(side="right")
        self.width_scale = ttk.Scale(self.frame, from_=100, to=2000, orient="horizontal", command=self.update_width)
        self.width_scale.pack(pady=10)
        self.width_scale.bind("<ButtonRelease-1>", self.save_width)
        self.editor.add_tooltip(self.width_scale, "Изменить ширину изображения")

        # Фрейм и элементы управления для высоты
        self.height_frame = ttk.Frame(self.frame)
        self.height_frame.pack(pady=10)
        self.height_label = ttk.Label(self.height_frame, text="Высота")
        self.height_label.pack(side="left")
        self.height_value_label = ttk.Label(self.height_frame, text="100")
        self.height_value_label.pack(side="right")
        self.height_scale = ttk.Scale(self.frame, from_=100, to=2000, orient="horizontal", command=self.update_height)
        self.height_scale.pack(pady=10)
        self.height_scale.bind("<ButtonRelease-1>", self.save_height)
        self.editor.add_tooltip(self.height_scale, "Изменить высоту изображения")

        # Кнопка для ручного ввода размеров
        self.manual_resize_button = ttk.Button(self.frame, text="Ввести размеры вручную", command=self.toggle_manual_resize_controls)
        self.manual_resize_button.pack(pady=10)
        self.editor.add_tooltip(self.manual_resize_button, "Изменить размеры изображения вручную")

        # Кнопка для поворота изображения
        self.rotate_button = ttk.Button(self.frame, text="Повернуть", command=self.toggle_rotate_controls)
        self.rotate_button.pack(pady=10)
        self.editor.add_tooltip(self.rotate_button, "Повернуть изображение")

        # Кнопка для обрезки изображения
        self.crop_button = ttk.Button(self.frame, text="Обрезать", command=self.editor.start_area_selection)
        self.crop_button.pack(pady=10)
        self.editor.add_tooltip(self.crop_button, "Обрезать изображение")

        # Фрейм для дополнительных элементов управления
        self.additional_controls_frame = ttk.Frame(self.editor.root)
        self.additional_controls_frame.pack(pady=10, fill='x')

    def update_width(self, event=None):
        # Обновление ширины изображения
        self.width_value_label.config(text=str(int(self.width_scale.get())))
        self.apply_adjustments()
        logging.info(f"Обновление ширины изображения: {self.width_scale.get()}")

    def update_height(self, event=None):
        # Обновление высоты изображения
        self.height_value_label.config(text=str(int(self.height_scale.get())))
        self.apply_adjustments()
        logging.info(f"Обновление высоты изображения: {self.height_scale.get()}")

    def apply_adjustments(self):
        # Применение изменений к изображению
        self.editor.apply_adjustments()

    def save_width(self, event):
        # Сохранение состояния после изменения ширины
        self.editor.save_history()
        logging.info("Сохранение истории после изменения ширины")

    def save_height(self, event):
        # Сохранение состояния после изменения высоты
        self.editor.save_history()
        logging.info("Сохранение истории после изменения высоты")

    def reset_sliders(self):
        # Сброс ползунков к значениям оригинального изображения
        self.width_scale.set(self.editor.original_image.width)
        self.height_scale.set(self.editor.original_image.height)
        self.width_value_label.config(text=str(self.editor.original_image.width))
        self.height_value_label.config(text=str(self.editor.original_image.height))
        logging.info("Сброс ползунков изменения размеров к оригинальным значениям")

    def clear_additional_controls(self):
        # Очистка дополнительных элементов управления
        for widget in self.additional_controls_frame.winfo_children():
            widget.destroy()

    def toggle_manual_resize_controls(self):
        # Переключение элементов управления для ручного ввода размеров
        if self.manual_resize_button.cget('text') == 'Скрыть размеры вручную':
            self.clear_additional_controls()
            self.manual_resize_button.config(text='Ввести размеры вручную')
            return

        self.clear_additional_controls()
        self.manual_resize_button.config(text='Скрыть размеры вручную')
        
        ttk.Label(self.additional_controls_frame, text="Ширина:", font=("Helvetica", 10)).grid(row=0, column=0)
        width_entry = Entry(self.additional_controls_frame)
        width_entry.grid(row=0, column=1)

        ttk.Label(self.additional_controls_frame, text="Высота:", font=("Helvetica", 10)).grid(row=1, column=0)
        height_entry = Entry(self.additional_controls_frame)
        height_entry.grid(row=1, column=1)

        def apply_manual_resize():
            # Применение ручного изменения размеров
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())
                if width >= 100 and height >= 100:
                    self.width_scale.set(width)
                    self.height_scale.set(height)
                    self.apply_adjustments()
                    self.editor.save_history()
                    self.clear_additional_controls()
                    self.manual_resize_button.config(text='Ввести размеры вручную')
                    logging.info(f"Применение ручного изменения размера: ширина {width}, высота {height}")
                else:
                    messagebox.showerror("Ошибка", "Ширина и высота должны быть больше 100")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные значения ширины и высоты")

        apply_button = ttk.Button(self.additional_controls_frame, text="Применить", command=apply_manual_resize)
        apply_button.grid(row=2, column=0, columnspan=2)

    def toggle_rotate_controls(self):
        # Переключение элементов управления для поворота изображения
        if self.rotate_button.cget('text') == 'Скрыть поворот':
            self.clear_additional_controls()
            self.rotate_button.config(text='Повернуть')
            return

        self.clear_additional_controls()
        self.rotate_button.config(text='Скрыть поворот')

        ttk.Label(self.additional_controls_frame, text="Угол поворота:", font=("Helvetica", 10)).grid(row=0, column=0)
        self.angle_entry = Entry(self.additional_controls_frame)
        self.angle_entry.grid(row=0, column=1)

        apply_button = ttk.Button(self.additional_controls_frame, text="Применить", command=self.apply_rotation)
        apply_button.grid(row=1, column=0, columnspan=2)

    def apply_rotation(self):
        # Применение поворота изображения
        try:
            angle = float(self.angle_entry.get())
            self.editor.image = self.editor.image.rotate(angle, expand=True)
            self.editor.original_image = self.editor.image.copy()  # Обновить оригинальное изображение
            self.editor.save_history()
            self.editor.update_display_image()
            self.clear_additional_controls()
            self.rotate_button.config(text='Повернуть')
            logging.info(f"Поворот изображения на угол: {angle}")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное значение угла")
