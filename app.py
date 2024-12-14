import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import zstandard as zstd
import os
import threading

class FileProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dosya İşlemleri Sistemi - By RageSawyer")
        self.root.geometry("600x500")

        self.dark_mode = self.load_dark_mode_setting()

        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(fill="both", expand=True)

        self.tab_control = ttk.Notebook(self.main_frame)
        self.tab_control.pack(fill="both", expand=True)

        self.setup_compress_tab()
        self.setup_search_tab()
        self.setup_clean_tab()

        self.dark_mode_button = tk.Button(self.main_frame, text="Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_button.pack(pady=10)

        self.status_label = tk.Label(self.main_frame, text="Durum: Bekleniyor...", font=("Arial", 10), anchor="w")
        self.status_label.pack(fill="x", pady=5)

        self.data_folder = "veriler"
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        self.apply_dark_mode()

    def load_dark_mode_setting(self):
        if os.path.exists("settings.txt"):
            with open("settings.txt", "r") as f:
                return f.read().strip() == "dark"
        return False

    def save_dark_mode_setting(self):
        with open("settings.txt", "w") as f:
            f.write("dark" if self.dark_mode else "light")

    def apply_dark_mode(self):
        bg_color = "#1e1e1e" if self.dark_mode else "SystemButtonFace"
        fg_color = "white" if self.dark_mode else "black"

        self.root.config(bg=bg_color)
        self.main_frame.config(bg=bg_color)
        self.status_label.config(bg=bg_color, fg=fg_color)
        self.dark_mode_button.config(bg=bg_color, fg=fg_color, text="Light Mode" if self.dark_mode else "Dark Mode")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=bg_color, foreground=fg_color)
        style.configure("TNotebook.Tab", background=bg_color, foreground=fg_color)

        for widget in self.main_frame.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                widget.config(bg=bg_color, fg=fg_color)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_dark_mode()
        self.save_dark_mode_setting()

    def setup_compress_tab(self):
        self.compress_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.compress_tab, text="Dosya Sıkıştır")

        compress_label = tk.Label(self.compress_tab, text="TXT Dosyasını Seç ve ZST'ye Çevir", font=("Arial", 12), bg="#1e1e1e", fg="white")
        compress_label.pack(pady=10)

        compression_label = tk.Label(self.compress_tab, text="Sıkıştırma Seviyesi (1-22):", bg="#1e1e1e", fg="white")
        compression_label.pack(pady=5)

        self.compression_level = tk.IntVar(value=5)
        compression_slider = tk.Scale(self.compress_tab, from_=1, to=22, orient="horizontal", variable=self.compression_level, bg="#1e1e1e", fg="white", troughcolor="#3e3e3e")
        compression_slider.pack(pady=5)

        compress_button = tk.Button(self.compress_tab, text="Dosya Seç", command=self.start_compression, bg="#1e1e1e", fg="white")
        compress_button.pack(pady=5)

        multi_compress_button = tk.Button(self.compress_tab, text="Çoklu Dosya Sıkıştır", command=self.start_multi_compression, bg="#1e1e1e", fg="white")
        multi_compress_button.pack(pady=5)

        self.upload_progress = ttk.Progressbar(self.compress_tab, orient="horizontal", length=400, mode="determinate")
        self.upload_progress.pack(pady=10)

    def start_compression(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return
        compression_thread = threading.Thread(target=self.compress_file, args=(file_path,))
        compression_thread.start()

    def compress_file(self, file_path):
        output_path = os.path.join(self.data_folder, os.path.basename(file_path) + ".zst")
        try:
            cctx = zstd.ZstdCompressor(level=self.compression_level.get())
            with open(file_path, "rb") as f, open(output_path, "wb") as o:
                total_size = os.path.getsize(file_path)
                processed_size = 0
                with cctx.stream_writer(o) as compressor:
                    while chunk := f.read(65536):
                        compressor.write(chunk)
                        processed_size += len(chunk)
                        self.upload_progress["value"] = (processed_size / total_size) * 100
                        self.root.update_idletasks()
            self.status_label.config(text=f"Başarılı: {output_path}")
        except Exception as e:
            self.status_label.config(text=f"Hata: {e}")

    def start_multi_compression(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt")])
        if not file_paths:
            return
        multi_compression_thread = threading.Thread(target=self.compress_multiple_files, args=(file_paths,))
        multi_compression_thread.start()

    def compress_multiple_files(self, file_paths):
        try:
            for file_path in file_paths:
                self.compress_file(file_path)
            self.status_label.config(text="Tüm dosyalar başarıyla sıkıştırıldı.")
        except Exception as e:
            self.status_label.config(text=f"Hata: {e}")

    def setup_search_tab(self):
        self.search_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.search_tab, text="Anahtar Kelime Ara")

        search_label = tk.Label(self.search_tab, text="Anahtar Kelimeler (virgülle ayır):", bg="#1e1e1e", fg="white")
        search_label.pack()

        self.keyword_entry = tk.Entry(self.search_tab, width=50, bg="#1e1e1e", fg="white")
        self.keyword_entry.pack(pady=5)

        search_button = tk.Button(self.search_tab, text="Ara", command=self.start_search, bg="#1e1e1e", fg="white")
        search_button.pack(pady=5)

        self.search_progress = ttk.Progressbar(self.search_tab, orient="horizontal", length=400, mode="determinate")
        self.search_progress.pack(pady=10)

        self.search_status_label = tk.Label(self.search_tab, text="Bulunan Sonuçlar: 0", font=("Arial", 10), bg="#1e1e1e", fg="white")
        self.search_status_label.pack(pady=5)

    def start_search(self):
        keywords = self.keyword_entry.get().strip()
        if not keywords:
            messagebox.showerror("Hata", "Lütfen bir veya birden fazla anahtar kelime girin.")
            return
        self.status_label.config(text="Durum: Arama yapılıyor...")
        self.search_status_label.config(text="Bulunan Sonuçlar: 0")
        keyword_list = [keyword.strip() for keyword in keywords.split(",") if keyword.strip()]
        search_thread = threading.Thread(target=self.search_keywords, args=(keyword_list,))
        search_thread.start()

    def search_keywords(self, keyword_list):
        try:
            zst_files = [os.path.join(self.data_folder, file) for file in os.listdir(self.data_folder) if file.endswith('.zst')]

            if not zst_files:
                self.status_label.config(text="Durum: Hiçbir .zst dosyası bulunamadı.")
                return

            self.search_progress['value'] = 0
            total_files = len(zst_files)
            results = []

            for index, zst_file in enumerate(zst_files):
                results.extend(self.decompress_and_search_keywords(zst_file, keyword_list))
                self.search_progress['value'] = ((index + 1) / total_files) * 100
                self.search_status_label.config(text=f"Bulunan Sonuçlar: {len(results)}")
                self.root.update_idletasks()

            if results:
                self.status_label.config(text="Durum: Arama tamamlandı.")
                self.show_results(results)
            else:
                self.status_label.config(text="Durum: Anahtar kelimeler bulunamadı.")
        except Exception as e:
            self.status_label.config(text=f"Hata: {e}")

    def decompress_and_search_keywords(self, zst_file, keyword_list):
        dctx = zstd.ZstdDecompressor()
        results = []
        try:
            with open(zst_file, 'rb') as compressed_file:
                with dctx.stream_reader(compressed_file) as decompressor:
                    buffer = decompressor.read(65536 * 2)
                    while buffer:
                        for line in buffer.splitlines():
                            try:
                                decoded_line = line.decode('utf-8')
                            except UnicodeDecodeError:
                                decoded_line = line.decode('latin-1')
                            if any(keyword.lower() in decoded_line.lower() for keyword in keyword_list):
                                results.append(f"{os.path.basename(zst_file)}: {decoded_line.strip()}")
                        buffer = decompressor.read(65536 * 2)
        except Exception as e:
            results.append(f"Hata ({zst_file}): {e}")
        return results

    def show_results(self, results):
        results_window = tk.Toplevel(self.root)
        results_window.title("Sonuçlar")

        frame = tk.Frame(results_window, bg="#1e1e1e")
        frame.pack(fill="both", expand=True)

        line_numbers = tk.Text(frame, width=5, padx=5, takefocus=0, border=0, background="#1e1e1e", foreground="white", state="disabled")
        line_numbers.pack(side="left", fill="y")

        text_area = tk.Text(frame, wrap=tk.WORD, undo=True, bg="#1e1e1e", fg="white")
        text_area.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, command=text_area.yview)
        scrollbar.pack(side="right", fill="y")
        text_area["yscrollcommand"] = scrollbar.set

        def update_line_numbers():
            line_numbers.config(state="normal")
            line_numbers.delete("1.0", "end")
            for i, line in enumerate(text_area.get("1.0", "end").splitlines(), start=1):
                line_numbers.insert("end", f"{i}\n")
            line_numbers.config(state="disabled")

        def on_text_change(event):
            update_line_numbers()

        text_area.bind("<KeyRelease>", on_text_change)
        text_area.insert("1.0", "\n".join(results))
        text_area.configure(state="normal")

        update_line_numbers()

        def select_line(event):
            line_index = line_numbers.index(f"@{event.x},{event.y}").split(".")[0]
            text_area.tag_remove("sel", "1.0", "end")
            text_area.tag_add("sel", f"{line_index}.0", f"{line_index}.end")
            text_area.mark_set("insert", f"{line_index}.0")
            text_area.see(f"{line_index}.0")

        line_numbers.bind("<Button-1>", select_line)

        search_frame = tk.Frame(results_window, bg="#1e1e1e")
        search_frame.pack(pady=5)

        search_label = tk.Label(search_frame, text="Ara:", bg="#1e1e1e", fg="white")
        search_label.grid(row=0, column=0, padx=5)

        search_entry = tk.Entry(search_frame, width=30, bg="#1e1e1e", fg="white")
        search_entry.grid(row=0, column=1, padx=5)

        replace_label = tk.Label(search_frame, text="Değiştir:", bg="#1e1e1e", fg="white")
        replace_label.grid(row=0, column=2, padx=5)

        replace_entry = tk.Entry(search_frame, width=30, bg="#1e1e1e", fg="white")
        replace_entry.grid(row=0, column=3, padx=5)

        def find_text():
            text_area.tag_remove("highlight", "1.0", "end")
            search_text = search_entry.get()
            if search_text:
                start_pos = "1.0"
                while True:
                    start_pos = text_area.search(search_text, start_pos, stopindex="end")
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(search_text)}c"
                    text_area.tag_add("highlight", start_pos, end_pos)
                    start_pos = end_pos
                text_area.tag_config("highlight", background="yellow")

        def replace_text():
            search_text = search_entry.get()
            replace_text = replace_entry.get()
            content = text_area.get("1.0", "end")
            new_content = content.replace(search_text, replace_text)
            text_area.delete("1.0", "end")
            text_area.insert("1.0", new_content)
            update_line_numbers()

        find_button = tk.Button(search_frame, text="Ara", command=find_text, bg="#1e1e1e", fg="white")
        find_button.grid(row=0, column=4, padx=5)

        replace_button = tk.Button(search_frame, text="Değiştir", command=replace_text, bg="#1e1e1e", fg="white")
        replace_button.grid(row=0, column=5, padx=5)

        save_button = tk.Button(results_window, text="Sonuçları Kaydet", command=lambda: self.save_results(text_area), bg="#1e1e1e", fg="white")
        save_button.pack(pady=5)

    def save_results(self, text_area):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text_area.get("1.0", "end").strip())
                messagebox.showinfo("Başarılı", f"Sonuçlar kaydedildi: {file_path}")
            except Exception as e:
                messagebox.showerror("Hata", f"Sonuçlar kaydedilemedi: {e}")

    def setup_clean_tab(self):
        self.clean_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.clean_tab, text="Aynı Satırları Temizle")

        clean_button = tk.Button(self.clean_tab, text="Temizle", command=self.start_cleaning, bg="#1e1e1e", fg="white")
        clean_button.pack(pady=5)

        self.clean_progress = ttk.Progressbar(self.clean_tab, orient="horizontal", length=400, mode="determinate")
        self.clean_progress.pack(pady=10)

    def start_cleaning(self):
        clean_thread = threading.Thread(target=self.clean_duplicates)
        clean_thread.start()

    def clean_duplicates(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = FileProcessingApp(root)
    root.mainloop()
