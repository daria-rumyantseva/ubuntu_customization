#!/usr/bin/env python3
"""
Прозрачная панель с движущимися изображениями - Pillow + GTK3
"""

import gi
import os
import tempfile
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib
from PIL import Image

class GhostPanel:
    def __init__(self):
        # Создаем прозрачное окно
        self.window = Gtk.Window()
        
        # Получаем размеры экрана
        screen = self.window.get_screen()
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Высота панели - 150 пикселей
        self.panel_height = 200
        
        # Устанавливаем размеры (во всю ширину внизу экрана)
        self.window.set_default_size(self.screen_width, self.panel_height)
        self.window.move(0, self.screen_height - self.panel_height)
        
        # Настройки прозрачного окна
        self.window.set_decorated(False)
        self.window.set_app_paintable(True)
        self.window.set_visual(self.window.get_screen().get_rgba_visual())
        
        # Делаем клики сквозными
        self.window.set_accept_focus(False)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_skip_pager_hint(True)
        self.window.set_keep_above(True)

        # CSS для полной прозрачности
        css = b"""
        window {
            background-color: rgba(0,0,0,0);
            background-image: none;
            border: none;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Контейнер для изображений
        self.fixed = Gtk.Fixed()
        self.window.add(self.fixed)
        
        # Список путей к изображениям
        self.image_paths = [
            "/home/dashulya/Изображения/фон/панелька/1.png",
            "/home/dashulya/Изображения/фон/панелька/2.png",
            "/home/dashulya/Изображения/фон/панелька/3.png",
            "/home/dashulya/Изображения/фон/панелька/4.png"
        ]
        
        # Загружаем все изображения
        self.images_data = []
        self.current_image_index = 0
        self.load_all_images()
        
        # Проверяем, что есть хотя бы одно изображение
        if not self.images_data:
            print("❌ Не удалось загрузить ни одного изображения!")
            return
        
        # Настройки анимации
        self.current_x = -self.images_data[0]["width"]  # Начинаем слева за экраном
        self.speed = 2
        
        # Создаем первое изображение
        self.current_image = self.images_data[0]["gtk_image"]
        y_position = (self.panel_height - self.images_data[0]["height"]) // 2
        self.fixed.put(self.current_image, self.current_x, y_position)
        
        # Запускаем анимацию
        GLib.timeout_add(16, self.move_image_horizontal)
        
        # Выход по правому клику
        self.window.connect("button-press-event", self.on_button_press)
        
        print("👻 Прозрачная GTK панель создана!")
        print(f"📏 Размер экрана: {self.screen_width}x{self.screen_height}")
        print(f"📏 Размер панели: {self.screen_width}x{self.panel_height}")
        print(f"🖼️  Загружено изображений: {len(self.images_data)}")
        print("🖱️  Правый клик для выхода")
        print(f"🚀 Начинаем с изображения 1")
        
    def load_all_images(self):
        """Загружаем все изображения через Pillow"""
        print("🔍 Начинаем загрузку изображений...")
        
        for i, image_path in enumerate(self.image_paths):
            print(f"\n📁 Обрабатываем изображение {i+1}:")
            print(f"   Путь: {image_path}")
            
            if not os.path.exists(image_path):
                print(f"   ❌ Файл не найден!")
                continue
                
            try:
                # Загружаем через Pillow
                with Image.open(image_path) as original_image:
                    print(f"   Размер оригинала: {original_image.size}")
                    print(f"   Формат: {original_image.format}")
                    print(f"   Режим: {original_image.mode}")
                    
                    # Сохраняем прозрачность для PNG изображений
                    if original_image.mode in ('RGBA', 'LA') or (original_image.mode == 'P' and 'transparency' in original_image.info):
                        print("   🔍 Обнаружена прозрачность, сохраняем альфа-канал")
                        # Конвертируем в RGBA для сохранения прозрачности
                        if original_image.mode != 'RGBA':
                            original_image = original_image.convert('RGBA')
                    else:
                        print("   🔍 Без прозрачности, используем RGB")
                        # Конвертируем в RGB для изображений без прозрачности
                        if original_image.mode != 'RGB':
                            original_image = original_image.convert('RGB')
                    
                    # Масштабируем под высоту панели
                    original_width, original_height = original_image.size
                    aspect_ratio = original_width / original_height
                    
                    image_height = self.panel_height - 20
                    image_width = int(image_height * aspect_ratio)
                    
                    print(f"   Масштабируем до: {image_width}x{image_height}")
                    
                    # Масштабируем с высоким качеством
                    resized_image = original_image.resize((image_width, image_height), Image.LANCZOS)
                    
                    # Конвертируем в формат для GTK
                    gtk_image = self.pillow_to_gtk_image(resized_image, original_image.mode)
                    
                    if gtk_image is not None:
                        image_data = {
                            "width": image_width,
                            "height": image_height,
                            "gtk_image": gtk_image
                        }
                        self.images_data.append(image_data)
                        print(f"   ✅ Изображение {i+1} успешно загружено")
                    else:
                        print(f"   ❌ Не удалось конвертировать изображение")
                    
            except Exception as e:
                print(f"   ❌ Ошибка загрузки: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n📊 Итог: загружено {len(self.images_data)} из {len(self.image_paths)} изображений")

    def pillow_to_gtk_image(self, pil_image, mode='RGB'):
        """Конвертирует изображение Pillow в Gtk.Image с сохранением прозрачности"""
        try:
            from gi.repository import GdkPixbuf
            import io
            
            # Определяем формат сохранения в зависимости от наличия альфа-канала
            if mode == 'RGBA':
                format_to_save = 'PNG'  # PNG поддерживает прозрачность
                print("   💎 Сохраняем с прозрачностью (PNG)")
            else:
                format_to_save = 'PNG'  # Все равно используем PNG для качества
                print("   💎 Сохраняем без прозрачности (PNG)")
            
            # Сохраняем изображение в буфер памяти
            buffer = io.BytesIO()
            pil_image.save(buffer, format=format_to_save)
            buffer.seek(0)
            
            # Создаем pixbuf из буфера
            loader = GdkPixbuf.PixbufLoader()
            loader.write(buffer.getvalue())
            loader.close()
            
            pixbuf = loader.get_pixbuf()
            
            # Создаем Gtk.Image из pixbuf
            gtk_image = Gtk.Image()
            gtk_image.set_from_pixbuf(pixbuf)
            
            return gtk_image
            
        except Exception as e:
            print(f"❌ Ошибка конвертации Pillow->GTK: {e}")
            return None
    
    def switch_to_next_image(self):
        """Переключаем на следующее изображение"""
        if len(self.images_data) <= 1:
            return self.images_data[0]["width"] if self.images_data else 100
            
        # Увеличиваем индекс текущего изображения
        self.current_image_index = (self.current_image_index + 1) % len(self.images_data)
        
        # Удаляем текущее изображение из контейнера
        self.fixed.remove(self.current_image)
        
        # Получаем данные следующего изображения
        next_image_data = self.images_data[self.current_image_index]
        self.current_image = next_image_data["gtk_image"]
        
        # Добавляем новое изображение в контейнер (начинаем слева за экраном)
        y_position = (self.panel_height - next_image_data["height"]) // 2
        self.fixed.put(self.current_image, -next_image_data["width"], y_position)
        
        # ВАЖНО: Показываем новое изображение
        self.current_image.show()
        
        print(f"🔄 Переключено на изображение {self.current_image_index + 1}")
        
        return next_image_data["width"]
    
    def move_image_horizontal(self):
        """Анимация движения слева направо с переключением изображений"""
        if not hasattr(self, 'images_data') or not self.images_data:
            return False
            
        current_image_data = self.images_data[self.current_image_index]
        
        # Обновляем позицию
        self.current_x += self.speed
        
        # Если текущее изображение полностью ушло за правый край
        if self.current_x > self.screen_width:
            # Переключаем на следующее изображение
            next_image_width = self.switch_to_next_image()
            # Начинаем новое изображение слева за экраном
            self.current_x = -next_image_width
        
        # Перемещаем изображение
        y_position = (self.panel_height - current_image_data["height"]) // 2
        self.fixed.move(self.current_image, self.current_x, y_position)
        
        return True
    
    def on_button_press(self, widget, event):
        """Обработчик кликов для выхода"""
        if event.button == 3:  # Правый клик
            print("👋 Выход...")
            Gtk.main_quit()
        return True
    
    def run(self):
        """Запуск приложения"""
        if not self.images_data:
            print("❌ Нечего показывать - нет изображений!")
            return
            
        self.window.show_all()
        Gtk.main()

if __name__ == "__main__":
    GhostPanel().run()
