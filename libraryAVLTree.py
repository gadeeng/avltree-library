import requests
import uuid

class Book:
    def __init__(self, title, author_name, author_id, release_year, isbn):
        self.title = title
        self.author_name = author_name
        self.author_id = author_id
        self.release_year = release_year
        self.isbn = isbn

    def __str__(self):
        return f'Title: {self.title}, Author: {self.author_name} (ID: {self.author_id}), Year: {self.release_year}, ISBN: {self.isbn}'

class AVLNode:
    def __init__(self, book):
        self.book = book
        self.left = None
        self.right = None
        self.height = 1

class LibraryAVL:
    def __init__(self):
        self.root = None
        self.author_index = {}
        self.author_name_to_id = {}

    def _height(self, node):
        return node.height if node else 0

    def _balance_factor(self, node):
        return self._height(node.left) - self._height(node.right) if node else 0

    def _update_height(self, node):
        if node:
            node.height = max(self._height(node.left), self._height(node.right)) + 1

    def _rotate_right(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        self._update_height(x)
        self._update_height(y)
        return y

    def insert_book(self, title, author_name, release_year, isbn, author_id=None):
        if author_id is None:
            author_id = str(uuid.uuid4())
        book = Book(title, author_name, author_id, release_year, isbn)
        self.root = self._insert(self.root, book)
        if author_id not in self.author_index:
            self.author_index[author_id] = []
        self.author_index[author_id].append(book)
        if author_name not in self.author_name_to_id:
            self.author_name_to_id[author_name] = []
        if author_id not in self.author_name_to_id[author_name]:
            self.author_name_to_id[author_name].append(author_id)

    def _insert(self, root, book):
        if not root:
            return AVLNode(book)
        if book.isbn < root.book.isbn:
            root.left = self._insert(root.left, book)
        elif book.isbn > root.book.isbn:
            root.right = self._insert(root.right, book)
        else:
            root.book = book
            return root
        self._update_height(root)
        balance = self._balance_factor(root)
        if balance > 1 and book.isbn < root.left.book.isbn:
            return self._rotate_right(root)
        if balance < -1 and book.isbn > root.right.book.isbn:
            return self._rotate_left(root)
        if balance > 1 and book.isbn > root.left.book.isbn:
            root.left = self._rotate_left(root.left)
            return self._rotate_right(root)
        if balance < -1 and book.isbn < root.right.book.isbn:
            root.right = self._rotate_right(root.right)
            return self._rotate_left(root)
        return root

    def insert_book_from_isbn(self, isbn):
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        try:
            response = requests.get(url)
            data = response.json()
            key = f"ISBN:{isbn}"
            if key not in data:
                print(f"Gagal menemukan data untuk ISBN: {isbn}")
                return
            book_data = data[key]
            title = book_data.get("title", "Unknown Title")
            authors = book_data.get("authors", [])
            author_name = authors[0]['name'] if authors else "Unknown Author"
            author_id = str(uuid.uuid4())
            publish_date = book_data.get("publish_date", "Unknown Year")
            try:
                release_year = int(publish_date.strip()[-4:])
            except:
                release_year = 0
            self.insert_book(title, author_name, release_year, isbn, author_id)
            print(f"Berhasil menambahkan: {title} oleh {author_name}")
        except Exception as e:
            print(f"Error mengambil data ISBN {isbn}: {e}")

    def search_by_title(self, title):
        result = []
        self._search_by_title(self.root, title, result)
        return result

    def _search_by_title(self, root, title, result):
        if not root:
            return
        if root.book.title.lower() == title.lower():
            result.append(root.book)
        self._search_by_title(root.left, title, result)
        self._search_by_title(root.right, title, result)

    def search_by_author_name(self, author_name):
        author_ids = self.author_name_to_id.get(author_name, [])
        result = []
        for author_id in author_ids:
            result.extend(self.author_index.get(author_id, []))
        return result

    def search_by_isbn(self, isbn):
        node = self._search_by_isbn(self.root, isbn)
        return node.book if node else None

    def _search_by_isbn(self, root, isbn):
        if not root or root.book.isbn == isbn:
            return root
        if isbn < root.book.isbn:
            return self._search_by_isbn(root.left, isbn)
        return self._search_by_isbn(root.right, isbn)
    
    def delete_book(self, isbn):
        book_node = self._search_by_isbn(self.root, isbn)
        if not book_node:
            print(f"Buku dengan ISBN {isbn} tidak ditemukan.")
            return

        book = book_node.book
        author_id = book.author_id
        author_name = book.author_name

        self.root = self._delete(self.root, isbn)

        if author_id in self.author_index:
            self.author_index[author_id] = [b for b in self.author_index[author_id] if b.isbn != isbn]
            if not self.author_index[author_id]:
                del self.author_index[author_id]

        if author_name in self.author_name_to_id:
            if author_id in self.author_name_to_id[author_name]:
                self.author_name_to_id[author_name].remove(author_id)
                if not self.author_name_to_id[author_name]:
                    del self.author_name_to_id[author_name]

        print(f"Berhasil menghapus buku dengan ISBN: {isbn}")

    def _delete(self, root, isbn):
        if not root:
            return root

        if isbn < root.book.isbn:
            root.left = self._delete(root.left, isbn)
        elif isbn > root.book.isbn:
            root.right = self._delete(root.right, isbn)
        else:
            if not root.left:
                temp = root.right
                root = None
                return temp
            elif not root.right:
                temp = root.left
                root = None
                return temp

            temp = self._get_min_value_node(root.right)
            root.book = temp.book
            root.right = self._delete(root.right, temp.book.isbn)

        if not root:
            return root

        self._update_height(root)

        balance = self._balance_factor(root)

        if balance > 1 and self._balance_factor(root.left) >= 0:
            return self._rotate_right(root)
        if balance > 1 and self._balance_factor(root.left) < 0:
            root.left = self._rotate_left(root.left)
            return self._rotate_right(root)
        if balance < -1 and self._balance_factor(root.right) <= 0:
            return self._rotate_left(root)
        if balance < -1 and self._balance_factor(root.right) > 0:
            root.right = self._rotate_right(root.right)
            return self._rotate_left(root)

        return root

    def _get_min_value_node(self, root):
        current = root
        while current.left:
            current = current.left
        return current
    
    def get_graphviz(self):
        from graphviz import Digraph
        dot = Digraph()

        def add_nodes_edges(node):
            if not node:
                return
            node_id = f"{node.book.isbn}"
            label = f"{node.book.title}\\n({node.book.isbn})"
            dot.node(node_id, label)

            if node.left:
                left_id = f"{node.left.book.isbn}"
                dot.edge(node_id, left_id)
                add_nodes_edges(node.left)
            if node.right:
                right_id = f"{node.right.book.isbn}"
                dot.edge(node_id, right_id)
                add_nodes_edges(node.right)
            
        add_nodes_edges(self.root)
        return dot
        


if __name__ == "__main__":
    library = LibraryAVL()

    isbn_list = [
        "0805062793",  # Buster
        "0743273567",  # The Great Gatsby
        "0143039563",  # The Adventures of Tom Sawyer
        "0553113461",  # Where no man has gone before
        "1404811796",  # Max goes to school
        "0805081984",  # Piper Reed, the great gypsy
        "9780141363950", # Dark Prophecy
        "9780807509135", # The Buddy Files
        "9780545442541", # One More Hug For Madison
        "9781847382078", # Ping Pong Pig
        "9780545350808", # Potty Time!
        "9780534393397", # Calculus tahun 2003
        "9780495467694", # Calculus tahun 2008
    ]

    print("Menambahkan buku dari API:")
    for isbn in isbn_list:
        library.insert_book_from_isbn(isbn)

    print("\nCari buku dengan judul:")
    for book in library.search_by_title("Calculus"):
        print(book)

    print("\nCari semua buku oleh penulis:")
    for book in library.search_by_author_name("Caroline Church"):
        print(book)

    print("\nCari buku berdasarkan ISBN:")
    book = library.search_by_isbn("0743273567")
    if book:
        print(book)
    else:
        print("Buku tidak ditemukan.")

    print("\nMenghapus buku dengan ISBN '0743273567':")
    library.delete_book("0743273567")

    print("\nCari buku berdasarkan ISBN setelah penghapusan:")
    book = library.search_by_isbn("0743273567")
    if book:
        print(book)
    else:
        print("Buku tidak ditemukan.")

    print("\nCari semua buku oleh penulis 'F. Scott Fitzgerald' setelah penghapusan:")
    for book in library.search_by_author_name("F. Scott Fitzgerald"):
        print(book)