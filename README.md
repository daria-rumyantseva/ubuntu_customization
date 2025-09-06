# Скрипты для кастомизации Ubuntu

Здесь хранятся скрипты для кастомизации Ubuntu.

## 📦 Установка

Скрипты необходимо поместить в каталог `/usr/local/bin/` и сделать исполняемыми:

```bash
sudo chmod +x /usr/local/bin/cherry
sudo chmod +x /usr/local/bin/berry
```

## 🚀 Использование

После установки скрипты можно запускать из командной строки:

```bash
cherry
berry
```

## ⚙️ Конфигурация

Оба скрипта используют конфигурационный файл:
```
$HOME/.cherry/config
```

**Содержание конфига:**
- Пути к рандомным обоям (для `cherry`)
- Пути к слайдшоу обоям (для `berry`)

## 📋 Зависимости

Для работы требуется установленное **pywal окружение**:
```
$HOME/.pywal-venv
```

## 🔧 Интеграция

В файл `$HOME/.bashrc` добавлены строки для:
- Корректной работы скриптов
- Автоматической смены цветовой схемы терминала
```
# export PATH=$PATH:~/.local/bin

export PATH="$PATH:/usr/local/bin/cherry"
export PATH="$PATH:/usr/local/bin/berry"

(cat ~/.cache/wal/sequences &)
source ~/.cache/wal/colors-tty.sh

echo "  ╱\\ 、  " 
echo " (˚ˎ 。7   "
echo " |、 ˜〵  "
echo " じしˍ,)ノ"

#source ~/.local/share/blesh/ble.sh
```
