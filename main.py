import logging
from tkinter import Tk
from ttkthemes import ThemedTk
from photo_editor import PhotoEditor
import os

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Запуск приложения")

    root = ThemedTk(theme="equilux")
    icon_path = os.path.join(os.path.dirname(__file__), 'image', 'frame.ico')
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    else:
        logging.warning(f"Иконка не найдена по пути {icon_path}. Убедитесь, что файл существует.")

    app = PhotoEditor(root)
    root.mainloop()
