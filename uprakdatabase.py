import tkinter as tk
from tkinter import ttk, messagebox
import pygame
from mysql.connector import connect, Error
from mutagen.mp3 import MP3

USERNAME = "Venrier"
PASSWORD = "smkn21"

db = connect(
    host="localhost",
    user="root",
    password="",
    database="market_21"
)

pygame.mixer.init()
is_paused = False
current_position = 0

def play_music():
    global current_position, is_paused
    pygame.mixer.music.load(r"C:\Users\PF3K2\OneDrive\Music\Playlists/LeeHi - ONLY (Lyrics).mp3")
    pygame.mixer.music.play(loops=-1, start=current_position)
    is_paused = False
    update_music_duration()

def pause_music():
    global current_position, is_paused
    pygame.mixer.music.pause()
    current_position = pygame.mixer.music.get_pos() / 1000
    is_paused = True

def unpause_music():
    global is_paused
    pygame.mixer.music.unpause()
    is_paused = False

def update_music_duration():
    if pygame.mixer.music.get_busy():
        total_duration = pygame.mixer.Sound(r"C:\Users\PF3K2\OneDrive\Music\Playlists").get_length()
        current_time = pygame.mixer.music.get_pos() / 1000
        label_duration.config(text=f"Current Time: {format_time(current_time)} / Total Duration: {format_time(total_duration)}")
        root.after(1000, update_music_duration)

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

def update_music_duration():
    global current_position
    if pygame.mixer.music.get_busy():
        audio = MP3(r"C:\Users\PF3K2\OneDrive\Music\Playlists/LeeHi - ONLY (Lyrics).mp3")
        total_duration = audio.info.length
        current_time = pygame.mixer.music.get_pos() / 1000
        

        if current_time >= total_duration:
            pygame.mixer.music.stop()
            label_duration.config(text="Musik Selesai")
            btn_play.config(state=tk.NORMAL)
            btn_pause.config(state=tk.DISABLED)
            btn_unpause.config(state=tk.DISABLED)
        else:
            label_duration.config(
                text=f"Current Time: {format_time(current_time)} / Total Duration: {format_time(total_duration)}"
            )
            root.after(1000, update_music_duration)

def login():
    username_input = entry_username.get()
    password_input = entry_password.get()

    if username_input == USERNAME and password_input == PASSWORD:
        messagebox.showinfo("Login Sukses", "Selamat datang!")
        login_window.destroy()
        main_app()
    else:
        messagebox.showerror("Login Gagal", "Username atau Password salah!")

def tambah_barang():
    kode_barang = entry_kode.get()
    nama_barang = entry_nama.get()
    try:
        harga_barang = int(entry_harga.get())
        stok_barang = int(entry_stok.get())
    except ValueError:
        messagebox.showerror("Input Error", "Harga dan Stok harus berupa angka!")
        return
    if not kode_barang or not nama_barang:
        messagebox.showerror("Input Error", "Kode Barang dan Nama Barang wajib diisi!")
        return
    try:
        cursor = db.cursor()
        query = """INSERT INTO barang_yang_dijual (kode_barang, nama_barang, harga_barang, stok_barang) VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (kode_barang, nama_barang, harga_barang, stok_barang))
        db.commit()
        messagebox.showinfo("Sukses", "Barang berhasil ditambahkan!")
        clear_entries()
        tampilkan_barang()
    except Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")

def hapus_barang():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Pilih barang yang ingin dihapus!")
        return

    kode_barang = tree.item(selected_item, "values")[0]
    confirm = messagebox.askyesno("Konfirmasi", f"Apakah Anda yakin ingin menghapus barang dengan kode {kode_barang}?")
    if confirm:
        try:
            cursor = db.cursor()
            query = "DELETE FROM barang_yang_dijual WHERE kode_barang = %s"
            cursor.execute(query, (kode_barang,))
            db.commit()
            messagebox.showinfo("Sukses", "Barang berhasil dihapus!")
            tampilkan_barang()
        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

def ubah_barang():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Pilih barang yang ingin diubah!")
        return
    kode_barang = tree.item(selected_item, "values")[0]
    nama_barang = entry_nama.get()
    try:
        harga_barang = int(entry_harga.get())
        stok_barang = int(entry_stok.get())
    except ValueError:
        messagebox.showerror("Input Error", "Harga dan Stok harus berupa angka!")
        return
    if not nama_barang:
        messagebox.showerror("Input Error", "Nama Barang wajib diisi!")
        return
    confirm = messagebox.askyesno("Konfirmasi", f"Apakah Anda yakin ingin mengubah data barang dengan kode {kode_barang}?")
    if confirm:
        try:
            cursor = db.cursor()
            query = """UPDATE barang_yang_dijual SET nama_barang = %s, harga_barang = %s, stok_barang = %s WHERE kode_barang = %s"""
            cursor.execute(query, (nama_barang, harga_barang, stok_barang, kode_barang))
            db.commit()
            messagebox.showinfo("Sukses", "Data barang berhasil diubah!")
            clear_entries()
            tampilkan_barang()
        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

def tampilkan_barang():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT kode_barang, nama_barang, harga_barang, stok_barang FROM barang_yang_dijual")
        records = cursor.fetchall()
        for row in tree.get_children():
            tree.delete(row)
        for i, record in enumerate(records):
            tag = 'odd' if i % 2 == 0 else 'even'
            tree.insert("", tk.END, values=record, tags=(tag,))
    except Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")


def cari_barang():
    keyword = entry_pencarian.get().strip()
    try:
        cursor = db.cursor()
        query = """
        SELECT kode_barang, nama_barang, harga_barang, stok_barang 
        FROM barang_yang_dijual 
        WHERE kode_barang LIKE %s OR nama_barang LIKE %s
        """
        search_pattern = f"%{keyword}%"
        cursor.execute(query, (search_pattern, search_pattern))
        records = cursor.fetchall()
        for row in tree.get_children():
            tree.delete(row)
        if records:
            for i, record in enumerate(records):
                tag = 'odd' if i % 2 == 0 else 'even'
                tree.insert("", tk.END, values=record, tags=(tag,))
            messagebox.showinfo("Pencarian", f"Ditemukan {len(records)} barang")
        else:
            messagebox.showinfo("Pencarian", "Tidak ada barang yang ditemukan")
    except Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")

def clear_entries():
    entry_kode.delete(0, tk.END)
    entry_nama.delete(0, tk.END)
    entry_harga.delete(0, tk.END)
    entry_stok.delete(0, tk.END)

def keluar_aplikasi():
    pygame.mixer.music.stop()
    db.close()
    root.destroy()

def main_app():
    global entry_kode, entry_nama, entry_harga, entry_stok, entry_pencarian, tree, root, label_duration
    global btn_play, btn_pause, btn_unpause

    root = tk.Tk()
    root.title("Aplikasi Database Barang")
    root.geometry("800x600")
    root.configure(bg="#f0f8ff")

    style = ttk.Style(root)
    style.theme_use("clam")

    header_label = tk.Label(root, text="Moeara Store", font=("Arial", 24, "bold"), fg="black", height=2)
    header_label.pack(fill="x")

    frame_input = tk.Frame(root, bg="#f0f8ff", pady=10)
    frame_input.pack(pady=10)

    font_label = ("Arial", 10, "bold")
    font_entry = ("Arial", 10)

    tk.Label(frame_input, text="Kode Barang:", font=font_label, bg="#f0f8ff").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_kode = tk.Entry(frame_input, font=font_entry, width=20)
    entry_kode.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    tk.Label(frame_input, text="Nama Barang:", font=font_label, bg="#f0f8ff").grid(row=0, column=2, padx=10, pady=5, sticky="e")
    entry_nama = tk.Entry(frame_input, font=font_entry, width=20)
    entry_nama.grid(row=0, column=3, padx=10, pady=5, sticky="w")

    tk.Label(frame_input, text="Harga Barang:", font=font_label, bg="#f0f8ff").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_harga = tk.Entry(frame_input, font=font_entry, width=20)
    entry_harga.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    tk.Label(frame_input, text="Stok Barang:", font=font_label, bg="#f0f8ff").grid(row=1, column=2, padx=10, pady=5, sticky="e")
    entry_stok = tk.Entry(frame_input, font=font_entry, width=20)
    entry_stok.grid(row=1, column=3, padx=10, pady=5, sticky="w")

    btn_tambah = tk.Button(frame_input, text="Tambah Barang", command=tambah_barang, bg="#4CAF50", fg="white", font=font_label, width=20)
    btn_tambah.grid(row=2, column=0, columnspan=2, pady=10)

    btn_hapus = tk.Button(frame_input, text="Hapus Barang", command=hapus_barang, bg="#f44336", fg="white", font=font_label, width=20)
    btn_hapus.grid(row=2, column=2, columnspan=2, pady=10)

    btn_ubah = tk.Button(frame_input, text="Ubah Barang", command=ubah_barang, bg="#2196F3", fg="white", font=font_label, width=20)
    btn_ubah.grid(row=3, column=0, columnspan=4, pady=10)

    frame_pencarian = tk.Frame(root, bg="#f0f8ff", pady=10)
    frame_pencarian.pack(pady=10)

    tk.Label(frame_pencarian, text="Cari Barang:", font=font_label, bg="#f0f8ff").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_pencarian = tk.Entry(frame_pencarian, font=font_entry, width=30)
    entry_pencarian.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    btn_cari = tk.Button(frame_pencarian, text="Cari", command=cari_barang, bg="#2196F3", fg="white", font=font_label, width=10)
    btn_cari.grid(row=0, column=2, padx=10, pady=5)

    btn_reset = tk.Button(frame_pencarian, text="Reset", command=tampilkan_barang, bg="#FF9800", fg="white", font=font_label, width=10)
    btn_reset.grid(row=0, column=3, padx=10, pady=5)

    frame_music = tk.Frame(root, bg="#f0f8ff", pady=10)
    frame_music.pack(pady=10, fill="x")

    frame_music.grid_columnconfigure(0, weight=1)
    frame_music.grid_columnconfigure(1, weight=1)
    frame_music.grid_columnconfigure(2, weight=1)

    btn_play = tk.Button(frame_music, text="▶️ Putar", command=play_music, bg="#4CAF50", fg="white", font=font_label)
    btn_play.grid(row=0, column=0, padx=10, pady=5)

    btn_pause = tk.Button(frame_music, text="⏸️ Jeda", command=pause_music, bg="#f44336", fg="white", font=font_label)
    btn_pause.grid(row=0, column=1, padx=10, pady=5)

    btn_unpause = tk.Button(frame_music, text="▶️ Lanjutkan", command=unpause_music, bg="#2196F3", fg="white", font=font_label)
    btn_unpause.grid(row=0, column=2, padx=10, pady=5)

    label_duration = tk.Label(frame_music, text="Current Time: 00:00 / Total Duration: 00:00", bg="#f0f8ff", font=font_label)
    label_duration.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")

    frame_table = tk.Frame(root, bg="#f0f8ff")
    frame_table.pack(pady=10, fill="both", expand=True)

    columns = ("Kode Barang", "Nama Barang", "Harga Barang", "Stok Barang")
    tree = ttk.Treeview(frame_table, columns=columns, show="headings")
    tree.heading("Kode Barang", text="Kode Barang")
    tree.heading("Nama Barang", text="Nama Barang")
    tree.heading("Harga Barang", text="Harga Barang")
    tree.heading("Stok Barang", text="Stok Barang")

    tree.column("Kode Barang", anchor="center", width=150, minwidth=150)
    tree.column("Nama Barang", anchor="center", width=200, minwidth=150)
    tree.column("Harga Barang", anchor="center", width=150, minwidth=150)
    tree.column("Stok Barang", anchor="center", width=150, minwidth=150)

    tree.tag_configure('odd', background="#f9f9f9")
    tree.tag_configure('even', background="#e9e9e9")

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    btn_keluar = tk.Button(root, text="Keluar", command=keluar_aplikasi, bg="#f44336", fg="white", font=font_label, width=20)
    btn_keluar.pack(pady=20)

    tampilkan_barang()

    root.mainloop()

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("400x300")
login_window.configure(bg="#f0f8ff")

font_title = ("Arial", 14, "bold")
font_label = ("Arial", 10)

tk.Label(login_window, text="Silakan Login", font=font_title, bg="#f0f8ff").pack(pady=20)
tk.Label(login_window, text="Username:", font=font_label, bg="#f0f8ff").pack()
entry_username = tk.Entry(login_window, font=("Arial", 10))
entry_username.pack(pady=5)

tk.Label(login_window, text="Password:", font=font_label, bg="#f0f8ff").pack()
entry_password = tk.Entry(login_window, show="*", font=("Arial", 10))
entry_password.pack(pady=5)

btn_login = tk.Button(login_window, text="Login", command=login, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
btn_login.pack(pady=20)

login_window.mainloop()
