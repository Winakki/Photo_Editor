import unittest
from unittest.mock import Mock, patch
from tkinter import Tk
from PIL import Image
from photo_editor import PhotoEditor

class TestPhotoEditor(unittest.TestCase):

    def setUp(self):
        self.patcher1 = patch('photo_editor.PhotoImage', new=Mock())
        self.patcher2 = patch('photo_editor.filedialog.askopenfilename', return_value='test_image.jpg')
        self.patcher3 = patch('photo_editor.Image.open')
        self.patcher4 = patch('tkinter.Tk', new_callable=Mock)

        self.mock_photoimage = self.patcher1.start()
        self.mock_askopenfilename = self.patcher2.start()
        self.mock_open = self.patcher3.start()
        self.mock_tk = self.patcher4.start()

        self.addCleanup(self.patcher1.stop)
        self.addCleanup(self.patcher2.stop)
        self.addCleanup(self.patcher3.stop)
        self.addCleanup(self.patcher4.stop)

        self.root = Tk()
        self.editor = PhotoEditor(self.root)
        self.mock_open.side_effect = [
            Image.new('RGB', (100, 100)),  # для image/undo.png
            Image.new('RGB', (100, 100)),  # для image/redo.png
            Image.new('RGB', (100, 100))   # для test_image.jpg
        ]
        self.editor.load_image_safe = Mock(return_value=Mock())
        self.editor.update_canvas_size = Mock()
        self.editor.update_display_image = Mock()
        self.editor.save_history = Mock()
        self.editor.set_slider_values = Mock()  # Замокировать set_slider_values
        self.editor.draw_tab.redraw_items = Mock()  # Замокировать redraw_items

    def test_load_image(self):
        # Проверка загрузки изображения
        self.editor.load_image('test_image.jpg')
        self.assertIsNotNone(self.editor.image)
        self.assertEqual(self.editor.image_path, 'test_image.jpg')
        self.editor.save_history.assert_called_once()  # Проверка вызова save_history
        self.mock_open.assert_any_call('test_image.jpg')
    
    @patch('photo_editor.filedialog.asksaveasfilename', return_value='test_save.jpg')
    @patch('photo_editor.Image.Image.save')
    def test_save_image(self, mock_save, mock_asksaveasfilename):
        # Проверка сохранения изображения
        self.editor.image = Image.new('RGB', (100, 100))
        self.editor.save_image('test_save.jpg')
        mock_save.assert_called_once_with('test_save.jpg')

    def test_undo(self):
        # Проверка отмены последнего действия
        self.editor.history.append((Image.new('RGB', (100, 100)), Image.new('RGB', (100, 100)), {"brightness": 1.0, "contrast": 1.0, "saturation": 1.0, "width": 100, "height": 100, "blur": 0}, [], []))
        self.editor.history.append((Image.new('RGB', (200, 200)), Image.new('RGB', (200, 200)), {"brightness": 1.0, "contrast": 1.0, "saturation": 1.0, "width": 200, "height": 200, "blur": 0}, [], []))
        self.editor.undo()
        self.assertEqual(len(self.editor.history), 1)
        self.assertEqual(len(self.editor.redo_stack), 1)
        self.editor.update_display_image.assert_called()
        self.editor.set_slider_values.assert_called()
        self.editor.draw_tab.redraw_items.assert_called()

    def test_redo(self):
        # Проверка повтора последнего отмененного действия
        self.editor.history.append((Image.new('RGB', (100, 100)), Image.new('RGB', (100, 100)), {"brightness": 1.0, "contrast": 1.0, "saturation": 1.0, "width": 100, "height": 100, "blur": 0}, [], []))
        self.editor.redo_stack.append((Image.new('RGB', (200, 200)), Image.new('RGB', (200, 200)), {"brightness": 1.0, "contrast": 1.0, "saturation": 1.0, "width": 200, "height": 200, "blur": 0}, [], []))
        self.editor.redo()
        self.assertEqual(len(self.editor.history), 2)
        self.assertEqual(len(self.editor.redo_stack), 0)
        self.editor.update_display_image.assert_called()
        self.editor.set_slider_values.assert_called()
        self.editor.draw_tab.redraw_items.assert_called()
    
    def test_apply_adjustments(self):
        # Проверка применения изменений к изображению
        self.editor.original_image = Image.new('RGB', (100, 100))
        self.editor.edit_tab.width_scale.get = Mock(return_value=200)
        self.editor.edit_tab.height_scale.get = Mock(return_value=200)
        self.editor.filter_tab.brightness_scale.get = Mock(return_value=1.0)
        self.editor.filter_tab.contrast_scale.get = Mock(return_value=1.0)
        self.editor.filter_tab.saturation_scale.get = Mock(return_value=1.0)
        self.editor.filter_tab.blur_scale.get = Mock(return_value=0)
        self.editor.apply_adjustments()
        self.editor.update_display_image.assert_called()
    
    def test_crop_image(self):
        # Проверка обрезки изображения
        self.editor.image = Image.new('RGB', (100, 100))
        self.editor.selection_top_x = 10
        self.editor.selection_top_y = 10
        self.editor.selection_bottom_x = 50
        self.editor.selection_bottom_y = 50
        self.editor.crop_image()
        self.assertEqual(self.editor.image.size, (40, 40))
        self.editor.update_canvas_size.assert_called()
        self.editor.update_display_image.assert_called()
        self.editor.save_history.assert_called()

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
