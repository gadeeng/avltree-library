import streamlit as st
from libraryAVLTree import LibraryAVL

st.set_page_config(page_title="AVL Library", page_icon="📚", layout="centered")

# Styling CSS untuk sidebar and content
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content h2 {
        color: #2c3e50;
        font-size: 24px;
        margin-bottom: 20px;
        text-align: center;
    }
    .sidebar .sidebar-content .stRadio > label {
        font-size: 18px;
        color: #34495e;
        padding: 10px;
        border-radius: 5px;
        transition: background-color 0.3s;
    }
    .sidebar .sidebar-content .stRadio > label:hover {
        background-color: #e0e0e0;
    }
    .sidebar .sidebar-content .stRadio > div > label > div {
        background-color: #3498db;
        border-radius: 50%;
    }
    .main .block-container {
        padding: 2rem;
        max-width: 800px;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Inisialisasi AVL Library
if 'library' not in st.session_state:
    st.session_state.library = LibraryAVL()

library = st.session_state.library

# Title
st.markdown("<h1 style='text-align: center; color: #ffffff'>📚 AVL Tree Library</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h2 style= 'color: #ffffff'>📚 AVL Library Menu</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = st.radio(
        "Pilih Menu",
        [
            "➕ Tambah Buku (dari ISBN)",
            "🔍 Cari Buku",
            "❌ Hapus Buku",
            "📖 Daftar Semua Buku",
            "🌳 Visualisasi AVL Tree"
        ],
        format_func=lambda x: x.split(" ")[0] + " " + " ".join(x.split(" ")[1:]),
    )
    
    st.markdown("---")
    st.markdown("**Tentang Aplikasi**")
    st.write("Aplikasi ini mengelola koleksi buku menggunakan struktur data AVL Tree." \
    "Gunakan menu untuk menambah, mencari, menghapus, atau memvisualisasikan buku.")
    st.markdown("**Dibuat oleh:** Kelompok 1 Struktur Data dan Algoritma")

# Display Book
def display_book(book):
    st.code(f"📖 {book.title}\n✍️  {book.author_name} ({book.release_year})\n🔢 ISBN: {book.isbn}", language="markdown")

# Logika berdasarkan menu
if menu == "➕ Tambah Buku (dari ISBN)":
    st.subheader("➕ Tambah Buku dari ISBN")
    with st.form("form_tambah"):
        isbn = st.text_input("📗 Masukkan ISBN:")
        submit = st.form_submit_button("Tambah Buku")

    if submit:
        with st.spinner("📡 Mengambil data dari OpenLibrary..."):
            existing_book = library.search_by_isbn(isbn)
            library.insert_book_from_isbn(isbn)
            new_book = library.search_by_isbn(isbn)

            if new_book and not existing_book:
                st.success(f"Buku dengan ISBN {isbn} berhasil ditambahkan!")
                display_book(new_book)
            elif existing_book:
                st.info(f"Buku dengan ISBN {isbn} sudah ada sebelumnya.")
                display_book(existing_book)
            else:
                st.warning("❌ Gagal menambahkan buku. ISBN tidak ditemukan.")

elif menu == "🔍 Cari Buku":
    st.subheader("🔍 Cari Buku")
    search_type = st.radio("Cari berdasarkan", ["Judul", "Penulis", "ISBN"])
    query = st.text_input("🔎 Masukkan kata kunci:")
    if st.button("Cari Buku"):
        if search_type == "Judul":
            results = library.search_by_title(query)
        elif search_type == "Penulis":
            results = library.search_by_author_name(query)
        elif search_type == "ISBN":
            result = library.search_by_isbn(query)
            results = [result] if result else []

        if results:
            st.success(f"📚 Ditemukan {len(results)} buku:")
            for book in results:
                display_book(book)
        else:
            st.warning("🔍 Buku tidak ditemukan.")

elif menu == "❌ Hapus Buku":
    st.subheader("❌ Hapus Buku berdasarkan ISBN")
    with st.form("form_hapus"):
        isbn = st.text_input("🗑️ Masukkan ISBN yang ingin dihapus:")
        hapus = st.form_submit_button("Hapus Buku")

    if hapus:
        before = library.search_by_isbn(isbn)
        library.delete_book(isbn)
        after = library.search_by_isbn(isbn)
        if before and not after:
            st.success(f"Buku dengan ISBN {isbn} berhasil dihapus.")
        else:
            st.warning("Buku tidak ditemukan atau gagal dihapus.")

elif menu == "📖 Daftar Semua Buku":
    st.subheader("📚 Semua Buku dalam AVL Tree")

    def inorder(node):
        if not node:
            return []
        return inorder(node.left) + [node.book] + inorder(node.right)

    all_books = inorder(library.root)
    if all_books:
        st.markdown(f"📦 Total buku: **{len(all_books)}**")
        for book in all_books:
            display_book(book)
    else:
        st.info("Belum ada buku dalam AVL Tree.")

elif menu == "🌳 Visualisasi AVL Tree":
    st.subheader("🌳 Struktur AVL Tree")
    dot = library.get_graphviz()
    if dot.source.strip():
        st.graphviz_chart(dot.source)
    else:
        st.info("AVL Tree masih kosong.")