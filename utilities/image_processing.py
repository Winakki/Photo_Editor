import logging
from PIL import Image, ImageEnhance, ImageFilter

def apply_adjustments(image, width, height, brightness, contrast, saturation, blur_radius):
    """
    Применяет настройки к изображению.

    Args:
        image (PIL.Image.Image): Исходное изображение.
        width (int): Новая ширина изображения.
        height (int): Новая высота изображения.
        brightness (float): Коэффициент яркости.
        contrast (float): Коэффициент контрастности.
        saturation (float): Коэффициент насыщенности.
        blur_radius (float): Радиус размытия.

    Returns:
        PIL.Image.Image: Измененное изображение.
    """
    logging.info(f"Применение настроек: ширина={width}, высота={height}, яркость={brightness}, контраст={contrast}, насыщенность={saturation}, размытие={blur_radius}")
    
    # Изменение размера изображения
    new_width = max(100, int(width))
    new_height = max(100, int(height))
    adjusted_image = image.resize((new_width, new_height), Image.LANCZOS)

    # Регулировка яркости
    enhancer = ImageEnhance.Brightness(adjusted_image)
    adjusted_image = enhancer.enhance(brightness)

    # Регулировка контрастности
    enhancer = ImageEnhance.Contrast(adjusted_image)
    adjusted_image = enhancer.enhance(contrast)

    # Регулировка насыщенности
    enhancer = ImageEnhance.Color(adjusted_image)
    adjusted_image = enhancer.enhance(saturation)

    # Применение размытия, если указано
    if blur_radius > 0:
        adjusted_image = adjusted_image.filter(ImageFilter.GaussianBlur(int(blur_radius)))

    return adjusted_image

def load_image(file_path):
    """
    Загружает изображение из файла.

    Args:
        file_path (str): Путь к изображению.

    Returns:
        PIL.Image.Image: Загруженное изображение.
    """
    logging.info(f"Загрузка изображения: {file_path}")
    try:
        return Image.open(file_path)
    except Exception as e:
        logging.error(f"Ошибка загрузки изображения {file_path}: {e}")
        raise

def save_image(image, save_path):
    """
    Сохраняет изображение в файл.

    Args:
        image (PIL.Image.Image): Изображение для сохранения.
        save_path (str): Путь для сохранения изображения.
    """
    logging.info(f"Сохранение изображения: {save_path}")
    try:
        image.save(save_path)
    except Exception as e:
        logging.error(f"Ошибка при сохранении изображения {save_path}: {e}")
        raise
