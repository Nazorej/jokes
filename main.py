# Это программа на Python
# Импортируем модули
import sqlite3
import random
import time
from PyQt5.QtWidgets import QApplication, QLabel, QDesktopWidget, QPushButton
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTime, QTimer
from datetime import datetime

# Подключаемся к базе данных anecdotes.db
conn = sqlite3.connect("anecdotes.db")
c = conn.cursor()

# Получаем список всех анекдотов
c.execute("SELECT text FROM anecdotes")
quotes = c.fetchall()

# Закрываем соединение с базой данных
conn.close()

# Создаем приложение PyQt
app = QApplication([])

# Создаем переменную для хранения интервала таймера в секундах (1800 секунд = 30 минут)
interval = 1800

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

x = x + 325
# Сдвинуть окно вправо на 50 пикселей

y = y - 140
# Приподнять окно вверх на 50 пикселей
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

# Создаем переменную для хранения состояния кнопки лайка
liked = False

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
        label.setText(f"{quote[0]}\n\nВы поставили лайк этому анекдоту!")

        # Меняем текст кнопки лайка на 👍
        like_button.setText("👍")

        # Меняем состояние кнопки лайка на True
        liked = True

    # Иначе, если анекдот уже был лайкнут
    else:

        # Обновляем поле liked в таблице истории для текущего анекдота
        c2.execute("UPDATE history SET liked = 0 WHERE text = ?", (quote[0],))
        conn2.commit()

        # Меняем текст кнопки лайка на 🐦
        like_button.setText("🐦")

        # Меняем состояние кнопки лайка на False
        liked = False

# Создаем функцию для обновления таймера
def update_timer():
    # Добавляем одну секунду к объекту времени
    time.addSecs(1)
    # Выводим время в формате MM:SS на метку
    label.setText(time.toString("mm:ss"))

# Связываем кнопку с функцией лайка
like_button.clicked.connect(like_quote)

# Создаем новую базу данных SQLite для сохранения истории
conn2 = sqlite3.connect("history.db")
c2 = conn2.cursor()

# Создаем таблицу для хранения истории с полем даты и времени
c2.execute("CREATE TABLE IF NOT EXISTS history (text TEXT, date_time TEXT, liked INTEGER)")
conn2.commit()

# Создаем функцию для обновления анекдотов
def update_quote():

    # Создаем объект времени с начальным значением 00:00:00
    time = QTime(0, 0, 0)

    # Объявляем переменную quote как глобальную, чтобы использовать ее в других функциях
    global quote

    # Выбираем случайный анекдот из списка
    quote = random.choice(quotes)

    # Выводим анекдот на метку
    label.setText(f"{quote[0]}")

    # Получаем текущую дату и время в формате YYYY-MM-DD HH:MM:SS
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Сохраняем анекдоты, дату и время в таблицу истории
    c2.execute("INSERT INTO history VALUES (?, ?, ?)", (quote[0], date_time, 0))
    conn2.commit()

def update_counter():
    # Уменьшаем значение интервала на единицу
    global interval; interval -= 1

    # Обновляем текст метки с добавлением счетчика в формате MM:SS
    label.setText(f"{quote[0]}\n\n{time.strftime('%M:%S', time.gmtime(interval))}")

# Создаем таймер PyQt для обновления анекдотов
timer = QTimer()

# Создаем таймер PyQt для обновления счетчика
counter_timer = QTimer()

# Устанавливаем интервал таймера счетчика в 100 миллисекунд
counter_timer.setInterval(100)

# Устанавливаем интервал таймера в 30 минут (1800000 миллисекунд)
timer.setInterval(1800000)

# Связываем таймер с функцией обновления счетчика
counter_timer.timeout.connect(update_counter)

# Запускаем таймер
counter_timer.start()

# Связываем таймер с функцией обновления анекдотов
timer.timeout.connect(update_quote)

# Запускаем таймер
timer.start()

# Обновляем анекдоты в первый раз
update_quote()

# Запускаем приложение PyQt
app.exec_()