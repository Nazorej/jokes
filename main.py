# Импортируем модули
import os
import random
import sqlite3
import sys
from datetime import datetime

from PyQt6 import QtWidgets, QtCore, QtGui

# Пути к файлам — рядом со скриптом, чтобы находились при любом запуске
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "favicon.jpg")
ANECDOTES_DB = os.path.join(BASE_DIR, "anecdotes.db")
HISTORY_DB = os.path.join(BASE_DIR, "history.db")

# Интервал смены анекдотов в секундах (1800 секунд = 30 минут)
INTERVAL = 1800

# Размер кнопок и размер значков на них
BUTTON_SIZE = 80
BUTTON_FONT_SIZE = 36


# Создаем класс для окна с анекдотами
class AnecdoteWindow(QtWidgets.QWidget):
    def __init__(self, quotes, history_conn):
        super().__init__()

        self.quotes = quotes                # список всех анекдотов
        self.history_conn = history_conn    # открытое соединение с базой истории
        self.deck = []                      # «колода» анекдотов — чтобы не повторялись
        self.current_text = ""              # текст текущего анекдота
        self.current_rowid = None           # id текущей записи в истории
        self.liked = False                  # поставлен ли лайк текущему анекдоту

        # Заголовок, размер и положение окна
        self.setWindowTitle("Анекдоты")
        self.setGeometry(825, 34, 620, 500)
        self.setStyleSheet("background-color: #272727;")

        # Создаем шрифт с заданным размером и жирностью для текста анекдотов
        font = QtGui.QFont()
        font.setPointSize(27)
        font.setBold(True)

        # Создаем метку для вывода анекдотов
        self.label = QtWidgets.QLabel()
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.label.setContentsMargins(10, 10, 10, 10)
        self.label.setStyleSheet("color: #FFFFFF;")

        # Оборачиваем метку в область с прокруткой, чтобы длинные анекдоты
        # не обрезались снизу — их можно будет дочитать, прокрутив текст
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)                       # метка тянется на всю область
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)  # без рамки вокруг текста
        # Горизонтальная прокрутка не нужна — текст переносится по словам
        self.scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Стилизуем полосу прокрутки под тёмный фон окна
        self.scroll_area.setStyleSheet("""
            QScrollArea { background-color: #272727; }
            QScrollBar:vertical { background: #272727; width: 12px; }
            QScrollBar::handle:vertical { background: #3a3a3a; border-radius: 6px; min-height: 40px; }
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical { height: 0; }
            QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical { background: none; }
        """)

        # Создаем шрифт для значков на кнопках — крупный, чтобы было видно
        button_font = QtGui.QFont()
        button_font.setPointSize(BUTTON_FONT_SIZE)

        # Создаем кнопку «новый анекдот» и кнопку лайка
        self.next_button = QtWidgets.QPushButton("🎲")
        self.next_button.setToolTip("Показать новый анекдот")

        self.like_button = QtWidgets.QPushButton("👍")
        self.like_button.setToolTip("Поставить / убрать лайк")

        for btn in (self.next_button, self.like_button):
            btn.setFont(button_font)
            btn.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
            btn.setStyleSheet("color: #FFFFFF; background-color: #3a3a3a; border-radius: 16px;")
            btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.next_button.clicked.connect(self.update_anecdote)
        self.like_button.clicked.connect(self.toggle_like)

        # Вертикальный компоновщик для кнопок — столбиком в правом верхнем углу
        buttons_layout = QtWidgets.QVBoxLayout()
        buttons_layout.addWidget(self.next_button)
        buttons_layout.addWidget(self.like_button)
        buttons_layout.addStretch(1)   # растяжка снизу прижимает кнопки к верху
        buttons_layout.setSpacing(12)  # расстояние между кнопками

        # Горизонтальный компоновщик всего окна: текст слева, кнопки справа
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(self.scroll_area, stretch=1)
        main_layout.addLayout(buttons_layout)

        # Таймер для автоматической смены анекдотов
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(INTERVAL * 1000)
        self.timer.timeout.connect(self.update_anecdote)
        self.timer.start()

        # Показываем первый анекдот сразу
        self.update_anecdote()

    # Функция берет случайный анекдот без повторов, пока все не покажутся
    def take_quote(self):
        if not self.deck:
            self.deck = random.sample(self.quotes, len(self.quotes))
            # Чтобы только что показанный анекдот не выпал первым в новом круге,
            # меняем его местами с началом новой колоды
            if len(self.deck) > 1 and self.deck[-1] == self.current_text:
                self.deck[0], self.deck[-1] = self.deck[-1], self.deck[0]
        return self.deck.pop()

    # Функция обновления анекдота
    def update_anecdote(self):
        self.current_text = self.take_quote()

        # Текущая дата и время в формате YYYY-MM-DD HH:MM:SS
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Сохраняем анекдот в историю и запоминаем id записи
        cur = self.history_conn.execute(
            "INSERT INTO history (text, date_time, liked) VALUES (?, ?, 0)",
            (self.current_text, date_time),
        )
        self.history_conn.commit()
        self.current_rowid = cur.lastrowid

        # Сбрасываем состояние кнопки лайка
        self.liked = False
        self.like_button.setText("👍")
        self.label.setText(self.current_text)
        # Прокручиваем текст к началу (если предыдущий анекдот прокрутили вниз)
        self.scroll_area.verticalScrollBar().setValue(0)

        # Перезапускаем таймер, чтобы 30 минут отсчитывались заново
        self.timer.start()

    # Функция для поставки и снятия лайка
    def toggle_like(self):
        self.liked = not self.liked

        # Обновляем поле liked только у текущей записи (по rowid)
        self.history_conn.execute(
            "UPDATE history SET liked = ? WHERE rowid = ?",
            (1 if self.liked else 0, self.current_rowid),
        )
        self.history_conn.commit()

        if self.liked:
            # ❤️ — сердечко с невидимым модификатором, чтобы рисовалось цветным,
            # а не чёрно-белым значком
            self.like_button.setText("❤️")
            self.label.setText(f"{self.current_text}\n\nВы поставили лайк этому анекдоту!")
        else:
            self.like_button.setText("👍")
            self.label.setText(self.current_text)

    # Функция вызывается при закрытии окна
    def closeEvent(self, event):
        # Останавливаем таймер и закрываем базу истории
        self.timer.stop()
        self.history_conn.close()
        super().closeEvent(event)


def main():
    # Проверяем, что база с анекдотами существует
    if not os.path.exists(ANECDOTES_DB):
        sys.exit(f"База данных не найдена: {ANECDOTES_DB}")

    # Читаем все анекдоты и сразу закрываем базу
    conn = sqlite3.connect(ANECDOTES_DB)
    try:
        rows = conn.execute("SELECT text FROM anecdotes").fetchall()
    except sqlite3.OperationalError:
        sys.exit("В anecdotes.db нет таблицы anecdotes")
    finally:
        conn.close()

    quotes = [row[0] for row in rows]
    if not quotes:
        sys.exit("Таблица anecdotes пуста — показывать нечего")

    # Соединение с базой истории держим открытым всё время работы программы,
    # закроем его при закрытии окна (closeEvent)
    history_conn = sqlite3.connect(HISTORY_DB)
    history_conn.execute(
        "CREATE TABLE IF NOT EXISTS history (text TEXT, date_time TEXT, liked INTEGER)"
    )
    history_conn.commit()

    # Создаем приложение и задаем иконку
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(ICON_PATH))

    # Создаем и показываем окно
    window = AnecdoteWindow(quotes, history_conn)
    window.show()

    # Запускаем главный цикл приложения
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
