# Это программа на Python
# Импортируем модули
import random
import time
from PyQt5.QtWidgets import QApplication, QLabel, QDesktopWidget, QPushButton
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTime, QTimer
from datetime import datetime
import sqlite3

# Создаем константу для хранения интервала таймера в секундах (1800 секунд = 30 минут)
INTERVAL = 1800

# Подключаемся к базе данных anecdotes.db
with sqlite3.connect("anecdotes.db") as conn:
    c = conn.cursor()

    # Получаем список всех анекдотов
    c.execute("SELECT text FROM anecdotes")
    quotes = c.fetchall()

# Создаем новую базу данных SQLite для сохранения истории
with sqlite3.connect("history.db") as conn2:
    c2 = conn2.cursor()

    # Создаем таблицу для хранения истории с полем даты и времени
    c2.execute("CREATE TABLE IF NOT EXISTS history (text TEXT, date_time TEXT, liked INTEGER)")
    conn2.commit()

# Создаем функцию для обновления анекдотов
def update_anecdote():

    # Объявляем переменную quote как глобальную, чтобы использовать ее в других функциях
    global quote

    # Присваиваем переменной quote случайный анекдот из списка quotes
    quote = random.choice(quotes)

    # Выводим анекдот на метку
    label.setText(quote[0])

    # Получаем текущую дату и время в формате YYYY-MM-DD HH:MM:SS
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Сохраняем анекдоты, дату и время в таблицу истории
    c2.execute("INSERT INTO history VALUES (?, ?, ?)", (quote[0], date_time, 0))
    conn2.commit()

# Создаем функцию для обработки нажатия на кнопку лайка
def like_quote():

    # Объявляем переменную liked как глобальную, чтобы использовать ее в других функциях
    global liked

    # Если анекдот еще не был лайкнут
    if not liked:

        # Обновляем поле liked в таблице истории для текущего анекдота
        c2.execute("UPDATE history SET liked = 1 WHERE text = ?", (quote[0],))
        conn2.commit()

        # Выводим сообщение об успешном лайке
        label.setText("{0}\n\nВы поставили лайк этому анекдоту!".format(quote[0]))

        # Меняем текст кнопки лайка на 👍
        like_button.setText("👍")

        # Меняем состояние кнопки лайка на True
        liked = True

    # Иначе, если анекдот уже был лайкнут
    else:

        # Обновляем поле liked в таблице истории для текущего анекдота
        c2.execute("UPDATE history SET liked = 0 WHERE text = ?", (quote[0],))
        conn2.commit()

        # Выводим анекдот без сообщения о лайке
        label.setText(quote[0])

        # Меняем текст кнопки лайка на 🐦
        like_button.setText("🐦")

        # Меняем состояние кнопки лайка на False
        liked = False

# Создаем приложение PyQt
app = QApplication([])

# Создаем метку для вывода анекдотов
label = QLabel()

# Уменьшаем окно по ширине и увеличиваем по высоте
label.resize(600, 300)

# Перемещаем окно немного выше центра экрана
screen = app.primaryScreen()
screen_size = screen.size()
window_size = label.size()
x = (screen_size.width() - window_size.width()) // 2
y = (screen_size.height() - window_size.height()) // 4
label.move(x, y)

# Показываем окно
label.show()

# Создаем шрифт с заданным размером и жирностью
font = QFont()
font.setPointSize(27)
font.setBold(True)

# Устанавливаем шрифт для метки
label.setFont(font)

# Сдвинуть окно вправо на 50 пикселей
x += 325

# Приподнять окно вверх на 50 пикселей
y -= 140

# Перемещаем окно
label.move(x, y)

# Включаем перенос текста по словам для метки
label.setWordWrap(True)

# Устанавливаем прозрачность окна
label.setWindowOpacity(1)

# Устанавливаем название окна - "Анекдоты"
label.setWindowTitle("Анекдоты")

# Устанавливаем иконку окна из файла favicon.jpg
icon = QIcon("favicon.jpg")
label.setWindowIcon(icon)

# Устанавливаем выравнивание текста по верхнему краю для метки
label.setAlignment(Qt.AlignTop)

# Устанавливаем отступ от краев окна в 20 пикселей для метки
label.setContentsMargins(20, 20, 60, 20)

# Устанавливаем цвет текста в белый для метки
label.setStyleSheet("color: #272727")

# Создаем кнопку для лайка анекдотов
like_button = QPushButton("🐦", label)

# Устанавливаем шрифт для кнопки
like_button.setFont(font)

# Устанавливаем размер кнопки
like_button.resize(50, 50)

# Перемещаем кнопку в правый нижний угол окна
like_button.move(label.width() - like_button.width() - 20, label.height() - like_button.height() - 20)

# Показываем кнопку
like_button.show()

# Перемещаем кнопку в правый верхний угол окна
like_button.move(label.width() - like_button.width() - 20, 20)

# Связываем кнопку с функцией лайка
like_button.clicked.connect(like_quote)

# Создаем переменную для хранения состояния кнопки лайка
liked = False

# Создаем таймер PyQt для обновления анекдотов
timer = QTimer()

# Связываем таймер с функцией обновления анекдотов
timer.timeout.connect(update_anecdote)

# Устанавливаем интервал таймера в интервал секунд (30 минут)
timer.setInterval(INTERVAL * 1000)

# Запускаем таймер для обновления анекдотов
timer.start()

# Обновляем анекдоты в первый раз
update_anecdote()

if __name__ == "__main__":
    # Запускаем приложение PyQt
    app.exec_()
