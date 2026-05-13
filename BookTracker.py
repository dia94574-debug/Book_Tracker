import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.books = []
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Фрейм для формы ввода
        input_frame = ttk.LabelFrame(self.root, text="Добавить книгу")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Поля ввода
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Автор:").grid(row=1, column=0, sticky="w")
        self.author_entry = ttk.Entry(input_frame, width=30)
        self.author_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Жанр:").grid(row=2, column=0, sticky="w")
        self.genre_entry = ttk.Entry(input_frame, width=30)
        self.genre_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Страниц:").grid(row=3, column=0, sticky="w")
        self.pages_entry = ttk.Entry(input_frame, width=30)
        self.pages_entry.grid(row=3, column=1, padx=5, pady=2)

        # Кнопка добавления
        add_button = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        add_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация")
        filter_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky="w")
        self.genre_filter = ttk.Combobox(filter_frame, values=["Все", "Фантастика", "Детектив", "Роман", "Научная литература"])
        self.genre_filter.set("Все")
        self.genre_filter.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(filter_frame, text="Страниц >:").grid(row=0, column=2, sticky="w")
        self.pages_filter = ttk.Entry(filter_frame, width=10)
        self.pages_filter.insert(0, "0")
        self.pages_filter.grid(row=0, column=3, padx=5, pady=2)

        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_button.grid(row=0, column=4, padx=5)

        # Таблица для отображения книг
        columns = ("Название", "Автор", "Жанр", "Страниц")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Кнопки сохранения/загрузки
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=3, column=0, padx=10, pady=5)

        save_button = ttk.Button(button_frame, text="Сохранить в JSON", command=self.save_data)
        save_button.pack(side=tk.LEFT, padx=5)

        load_button = ttk.Button(button_frame, text="Загрузить из JSON", command=self.load_data)
        load_button.pack(side=tk.LEFT, padx=5)
        

    def validate_input(self):
        """Проверка корректности ввода"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages = self.pages_entry.get().strip()

        if not title or not author or not genre:
            messagebox.showerror("Ошибка", "Все поля, кроме количества страниц, должны быть заполнены!")
            return False

        try:
            pages_num = int(pages)
            if pages_num <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")
            return False

        return True, title, author, genre, pages_num

    def add_book(self):
        """Добавление книги в список"""
        validation_result = self.validate_input()
        if not validation_result:
            return

        is_valid, title, author, genre, pages = validation_result

        book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(book)

        # Очистка полей ввода
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

        self.update_table()
        messagebox.showinfo("Успех", "Книга добавлена!")

    def update_table(self):
        """Обновление таблицы с книгами"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for book in self.books:
            self.tree.insert("", tk.END, values=(
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))

    def apply_filter(self):
        """Применение фильтров к списку книг"""
        selected_genre = self.genre_filter.get()
        try:
            min_pages = int(self.pages_filter.get())
        except ValueError:
            min_pages = 0

        filtered_books = self.books

        if selected_genre != "Все":
            filtered_books = [book for book in filtered_books if book["genre"] == selected_genre]

        filtered_books = [book for book in filtered_books if book["pages"] >= min_pages]

        # Обновление таблицы с отфильтрованными данными
        for item in self.tree.get_children():
            self.tree.delete(item)

        for book in filtered_books:
            self.tree.insert("", tk.END, values=(
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))

    def save_data(self):
        """Сохранение данных в JSON-файл"""
        with open("books.json", "w", encoding="utf-8") as f:
            json.dump(self.books, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Успех", "Данные сохранены в books.json!")


    def load_data(self):
        """Загрузка данных из JSON-файла"""
        try:
            if os.path.exists("books.json"):
                with open("books.json", "r", encoding="utf-8") as f:
                    self.books = json.load(f)
                self.update_table()
                messagebox.showinfo("Успех", "Данные загружены из books.json!")
            else:
                # Создаём пустой файл, если его нет
                with open("books.json", "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
                self.books = []
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()
