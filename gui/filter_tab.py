import logging
from tkinter import ttk
from utilities.image_processing import apply_adjustments

class FilterTab:
    def __init__(self, notebook, editor):
        logging.info("Инициализация FilterTab")
        self.editor = editor
        self.frame = ttk.Frame(notebook, style="TFrame")

        # Фрейм и элементы управления для яркости
        self.brightness_frame = ttk.Frame(self.frame)
        self.brightness_frame.pack(pady=10)
        self.brightness_label = ttk.Label(self.brightness_frame, text="Яркость")
        self.brightness_label.pack(side="left")
        self.brightness_value_label = ttk.Label(self.brightness_frame, text="1.0")
        self.brightness_value_label.pack(side="right")
        self.brightness_scale = ttk.Scale(self.frame, from_=0.5, to=2.0, orient="horizontal", command=self.update_brightness)
        self.brightness_scale.set(1.0)
        self.brightness_scale.pack(pady=10)
        self.brightness_scale.bind("<ButtonRelease-1>", self.save_brightness)
        self.editor.add_tooltip(self.brightness_scale, "Регулировка яркости изображения")

        # Фрейм и элементы управления для контрастности
        self.contrast_frame = ttk.Frame(self.frame)
        self.contrast_frame.pack(pady=10)
        self.contrast_label = ttk.Label(self.contrast_frame, text="Контрастность")
        self.contrast_label.pack(side="left")
        self.contrast_value_label = ttk.Label(self.contrast_frame, text="1.0")
        self.contrast_value_label.pack(side="right")
        self.contrast_scale = ttk.Scale(self.frame, from_=0.5, to=2.0, orient="horizontal", command=self.update_contrast)
        self.contrast_scale.set(1.0)
        self.contrast_scale.pack(pady=10)
        self.contrast_scale.bind("<ButtonRelease-1>", self.save_contrast)
        self.editor.add_tooltip(self.contrast_scale, "Регулировка контрастности изображения")

        # Фрейм и элементы управления для насыщенности
        self.saturation_frame = ttk.Frame(self.frame)
        self.saturation_frame.pack(pady=10)
        self.saturation_label = ttk.Label(self.saturation_frame, text="Насыщенность")
        self.saturation_label.pack(side="left")
        self.saturation_value_label = ttk.Label(self.saturation_frame, text="1.0")
        self.saturation_value_label.pack(side="right")
        self.saturation_scale = ttk.Scale(self.frame, from_=0.5, to=2.0, orient="horizontal", command=self.update_saturation)
        self.saturation_scale.set(1.0)
        self.saturation_scale.pack(pady=10)
        self.saturation_scale.bind("<ButtonRelease-1>", self.save_saturation)
        self.editor.add_tooltip(self.saturation_scale, "Регулировка насыщенности изображения")

        # Фрейм и элементы управления для размытия
        self.blur_frame = ttk.Frame(self.frame)
        self.blur_frame.pack(pady=10)
        self.blur_label = ttk.Label(self.blur_frame, text="Размытие")
        self.blur_label.pack(side="left")
        self.blur_value_label = ttk.Label(self.blur_frame, text="0")
        self.blur_value_label.pack(side="right")
        self.blur_scale = ttk.Scale(self.frame, from_=0, to=10, orient="horizontal", command=self.update_blur)
        self.blur_scale.pack(pady=10)
        self.blur_scale.bind("<ButtonRelease-1>", self.save_blur)
        self.editor.add_tooltip(self.blur_scale, "Регулировка размытия изображения")

    def update_brightness(self, event=None):
        # Обновление яркости изображения
        if hasattr(self.editor, 'image') and self.editor.image is not None:
            self.brightness_value_label.config(text=f"{self.brightness_scale.get():.1f}")
            self.apply_adjustments()

    def update_contrast(self, event=None):
        # Обновление контрастности изображения
        if hasattr(self.editor, 'image') and self.editor.image is not None:
            self.contrast_value_label.config(text=f"{self.contrast_scale.get():.1f}")
            self.apply_adjustments()

    def update_saturation(self, event=None):
        # Обновление насыщенности изображения
        if hasattr(self.editor, 'image') and self.editor.image is not None:
            self.saturation_value_label.config(text=f"{self.saturation_scale.get():.1f}")
            self.apply_adjustments()

    def update_blur(self, event=None):
        # Обновление размытия изображения
        if hasattr(self.editor, 'image') and self.editor.image is not None:
            self.blur_value_label.config(text=str(int(self.blur_scale.get())))
            self.apply_adjustments()

    def apply_adjustments(self):
        # Применение изменений к изображению
        if hasattr(self.editor, 'image') and self.editor.image is not None:
            self.editor.apply_adjustments()

    def save_brightness(self, event):
        # Сохранение состояния после изменения яркости
        if hasattr(self.editor, 'image') and self.editor.image is not None:
            self.editor.save_history()

    def save_contrast(self, event):
        # Сохранение состояния после изменения контрастности
        if hasattr(self.editor, 'image') and self.editor.image is not None:
            self.editor.save_history()

    def save_saturation(self, event):
        # Сохранение состояния после изменения насыщенности
        if hasattr(self.editor, 'image') and self.editor.image is not None:
            self.editor.save_history()

    def save_blur(self, event):
        # Сохранение состояния после изменения размытия
        if hasattr(self.editor, 'image') and self.editor.image is not None:
            self.editor.save_history()
    
    def reset_sliders(self):
        # Сброс ползунков к значениям по умолчанию
        self.brightness_scale.set(1.0)
        self.contrast_scale.set(1.0)
        self.saturation_scale.set(1.0)
        self.blur_scale.set(0.0)
        self.brightness_value_label.config(text="1.0")
        self.contrast_value_label.config(text="1.0")
        self.saturation_value_label.config(text="1.0")
        self.blur_value_label.config(text="0.0")
