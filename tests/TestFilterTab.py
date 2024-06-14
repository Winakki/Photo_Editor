import unittest
from unittest.mock import Mock
from tkinter import Tk
from photo_editor import PhotoEditor
from gui.filter_tab import FilterTab

class TestFilterTab(unittest.TestCase):

    def setUp(self):
        self.root = Tk()
        self.mock_editor = Mock()
        self.mock_editor.root = self.root
        self.mock_editor.image = Mock()
        self.filter_tab = FilterTab(self.root, self.mock_editor)

    def tearDown(self):
        self.root.destroy()

    def test_initialization(self):
        # Проверка инициализации вкладки фильтров
        self.assertIsNotNone(self.filter_tab.frame)
        self.assertIsNotNone(self.filter_tab.brightness_scale)
        self.assertIsNotNone(self.filter_tab.contrast_scale)
        self.assertIsNotNone(self.filter_tab.saturation_scale)
        self.assertIsNotNone(self.filter_tab.blur_scale)

    def test_update_brightness(self):
        # Проверка обновления яркости изображения
        self.filter_tab.brightness_scale.set(1.5)
        self.filter_tab.update_brightness()
        self.assertEqual(self.filter_tab.brightness_value_label.cget('text'), "1.5")
        self.mock_editor.apply_adjustments.assert_called()

    def test_update_contrast(self):
        # Проверка обновления контрастности изображения
        self.filter_tab.contrast_scale.set(1.5)
        self.filter_tab.update_contrast()
        self.assertEqual(self.filter_tab.contrast_value_label.cget('text'), "1.5")
        self.mock_editor.apply_adjustments.assert_called()

    def test_update_saturation(self):
        # Проверка обновления насыщенности изображения
        self.filter_tab.saturation_scale.set(1.5)
        self.filter_tab.update_saturation()
        self.assertEqual(self.filter_tab.saturation_value_label.cget('text'), "1.5")
        self.mock_editor.apply_adjustments.assert_called()

    def test_update_blur(self):
        # Проверка обновления размытия изображения
        self.filter_tab.blur_scale.set(5)
        self.filter_tab.update_blur()
        self.assertEqual(self.filter_tab.blur_value_label.cget('text'), "5")
        self.mock_editor.apply_adjustments.assert_called()

    def test_save_brightness(self):
        # Проверка сохранения состояния после изменения яркости
        self.filter_tab.save_brightness(None)
        self.mock_editor.save_history.assert_called()

    def test_save_contrast(self):
        # Проверка сохранения состояния после изменения контрастности
        self.filter_tab.save_contrast(None)
        self.mock_editor.save_history.assert_called()

    def test_save_saturation(self):
        # Проверка сохранения состояния после изменения насыщенности
        self.filter_tab.save_saturation(None)
        self.mock_editor.save_history.assert_called()

    def test_save_blur(self):
        # Проверка сохранения состояния после изменения размытия
        self.filter_tab.save_blur(None)
        self.mock_editor.save_history.assert_called()

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)