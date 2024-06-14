import unittest
from unittest.mock import Mock, patch
from tkinter import Tk, Entry
from photo_editor import PhotoEditor
from gui.edit_tab import EditTab

class TestEditTab(unittest.TestCase):

    def setUp(self):
        self.root = Tk()
        self.mock_editor = Mock(spec=PhotoEditor)
        self.mock_editor.root = self.root  # Добавляем атрибут root
        self.mock_editor.image = Mock()  # Замокировать атрибут image
        self.edit_tab = EditTab(self.root, self.mock_editor)

    def test_initialization(self):
        # Проверка инициализации вкладки редактирования
        self.assertIsInstance(self.edit_tab, EditTab)
        self.assertIsNotNone(self.edit_tab.frame)
        self.assertEqual(self.edit_tab.width_value_label.cget('text'), '100')
        self.assertEqual(self.edit_tab.height_value_label.cget('text'), '100')

    def test_update_width(self):
        # Проверка обновления ширины изображения
        self.edit_tab.width_scale.set(500)
        self.edit_tab.update_width()
        self.assertEqual(self.edit_tab.width_value_label.cget('text'), '500')
        self.mock_editor.apply_adjustments.assert_called()

    def test_update_height(self):
        # Проверка обновления высоты изображения
        self.edit_tab.height_scale.set(500)
        self.edit_tab.update_height()
        self.assertEqual(self.edit_tab.height_value_label.cget('text'), '500')
        self.mock_editor.apply_adjustments.assert_called()

    def test_save_width(self):
        # Проверка сохранения состояния после изменения ширины
        event = Mock()
        self.edit_tab.save_width(event)
        self.mock_editor.save_history.assert_called()

    def test_save_height(self):
        # Проверка сохранения состояния после изменения высоты
        event = Mock()
        self.edit_tab.save_height(event)
        self.mock_editor.save_history.assert_called()

    @patch('tkinter.Entry', new_callable=Mock)
    @patch('tkinter.messagebox.showerror')
    def test_apply_manual_resize_invalid(self, mock_showerror, mock_entry):
        # Проверка ручного изменения размеров с некорректными значениями
        mock_entry.return_value.get.side_effect = ['invalid', 'invalid']
        self.edit_tab.toggle_manual_resize_controls()
        self.edit_tab.apply_manual_resize = Mock()
        self.edit_tab.additional_controls_frame.children['!button'].invoke()
        self.edit_tab.apply_manual_resize()
        mock_showerror.assert_called()

    @patch('tkinter.Entry', new_callable=Mock)
    @patch('tkinter.messagebox.showerror')
    def test_apply_rotation_invalid(self, mock_showerror, mock_entry):
        # Проверка поворота изображения с некорректными значениями угла
        mock_entry.return_value.get.side_effect = ['invalid']
        self.edit_tab.toggle_rotate_controls()
        self.edit_tab.apply_rotation = Mock()
        self.edit_tab.additional_controls_frame.children['!button'].invoke()
        self.edit_tab.apply_rotation()
        mock_showerror.assert_called()

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
        
