import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import messagebox, filedialog, Toplevel, Label, Entry, Button
import os
import tempfile
from youtube_tool import bot_ytb
import threading

def select_file(file_path_label, file_type):
    file_path = filedialog.askopenfilename(filetypes=[(f"{file_type} files", f"*.{file_type}")])
    if file_path:
        file_path_label.config(text=file_path)
    
def on_drop(event, file_path_label, file_type):
    file_path = event.data.strip("{}")
    if file_path.endswith(f".{file_type}"):
        file_path_label.config(text=file_path)
    else:
        messagebox.showwarning("Warning", f"Vui lòng kéo thả file {file_type}.")

def open_settings(tk):
    # Tạo cửa sổ con (cửa sổ cài đặt)
    settings_window = Toplevel(root)
    settings_window.title("Cài đặt chương trình")
    settings_window.geometry("400x350")

    temp_settings_dir = f"{tempfile.gettempdir()}\\ybt_bot\\settings"
    if not os.path.exists(temp_settings_dir):
        os.makedirs(temp_settings_dir)
    

    # Cài đặt 1: File secrets
    secrets_file_frame = tk.Frame(settings_window, padx=10, pady=10)
    secrets_file_frame.pack(fill="x")

    secrets_file_label = tk.Label(secrets_file_frame, text="Kéo thả file secrets vào đây:", font=("Arial", 12))
    secrets_file_label.pack(anchor="w")

    secrets_file_path = tk.Label(secrets_file_frame, text="", bg="white", relief="sunken", height=2)
    secrets_file_path.pack(pady=5, fill="x")

    secrets_file_path.drop_target_register(DND_FILES)
    secrets_file_path.dnd_bind("<<Drop>>", lambda event: on_drop(event, secrets_file_path, "json"))

    secrets_file_button = tk.Button(secrets_file_frame, text="Chọn file", command=lambda: select_file(secrets_file_path, "json"))
    secrets_file_button.pack(pady=5)

    client_secrets_file = 'client_secret.json'
    # check if the file exists in temp_settings_dir
    if os.path.exists(f"{temp_settings_dir}\\{client_secrets_file}"):
        secrets_file_path.config(text=client_secrets_file)


    # Cài đặt 2: Thư mục HAR và Cookies
    har_file_frame = tk.Frame(settings_window, padx=10, pady=10)
    har_file_frame.pack(fill="x")

    har_file_label = tk.Label(har_file_frame, text="Kéo thả file har vào đây:", font=("Arial", 12))
    har_file_label.pack(anchor="w")

    har_file_path = tk.Label(har_file_frame, text="", bg="white", relief="sunken", height=2)
    har_file_path.pack(pady=5, fill="x")

    har_file_path.drop_target_register(DND_FILES)
    har_file_path.dnd_bind("<<Drop>>", lambda event: on_drop(event, har_file_path, "har"))

    har_file_button = tk.Button(har_file_frame, text="Chọn file", command=lambda: select_file(har_file_path, "har"))
    har_file_button.pack(pady=5)


    har_dir = f"{temp_settings_dir}\\har_and_cookies"
    if not os.path.exists(har_dir):
        os.makedirs(har_dir)
    chatgpt_har_file = 'chatgpt_com.har'
    if os.path.exists(f"{har_dir}\\{chatgpt_har_file}"):
        har_file_path.config(text=chatgpt_har_file)

    # Nút lưu cài đặt
    def save_settings():
        secrets_file = secrets_file_path.cget("text")
        har_file = har_file_path.cget("text")

        if secrets_file and har_file:
            if secrets_file != client_secrets_file:
                new_secrets_file = f"{temp_settings_dir}\\{client_secrets_file}"
                secrets_file = os.path.normpath(secrets_file)
                os.system(f"copy {secrets_file} {new_secrets_file}")
            if har_file != chatgpt_har_file:
                new_har_file = f"{har_dir}\\{chatgpt_har_file}"
                har_file = os.path.normpath(har_file)
                os.system(f"copy {har_file} {new_har_file}")
            messagebox.showinfo("Success", "Lưu cài đặt thành công.")
        else:
            messagebox.showwarning("Warning", "Vui lòng chọn file secrets và file HAR.")
    
    def close_settings():
        settings_window.destroy()  

    Button(settings_window, text="Lưu cài đặt", command=save_settings).pack(side="left", padx=10)
    Button(settings_window, text="Đóng", command=close_settings, width=10).pack(side="right", padx=10)

def process_file(tk, logging_text, running, video_id, process_button):
    video_id = video_id.get()
    running[0] = True
    process_button.config(state=tk.DISABLED)
    threading.Thread(target=bot_ytb, args=(tk, logging_text, running, video_id), daemon=True).start()

def stop_processing(running, process_button):
    running[0] = False
    process_button.config(state=tk.NORMAL)

def close_app():
    root.destroy()

if __name__ == '__main__':
    try:
        # Tạo cửa sổ Tkinter với TkinterDnD
        root = TkinterDnD.Tk()
        root.title("Bot Youtube Tool")

        setting_frame = tk.Frame(root, padx=10, pady=10)
        setting_frame.pack(fill="x")

        settings_button = tk.Button(setting_frame, text="Cài đặt", command=lambda: open_settings(tk), width=10)
        settings_button.pack(pady=10, side="right", padx=10)

        # Nhập video id
        video_id_frame = tk.Frame(root, padx=10, pady=10)
        video_id_frame.pack(fill="x")

        video_id_label = tk.Label(video_id_frame, text="Nhập video id:", font=("Arial", 12))
        video_id_label.pack(anchor="w", side="left")

        video_id = tk.Entry(video_id_frame, width=50)
        video_id.pack(pady=5, fill="x", ipady=4, side="right", padx=10) 

        # logging frame
        logging_frame = tk.Frame(root, padx=10, pady=10)
        logging_frame.pack(fill="x")

        logging_label = tk.Label(logging_frame, text="App logs:", font=("Arial", 12))
        logging_label.pack(anchor="w")

        logging_text = tk.Text(logging_frame, height=10, width=50)
        logging_text.pack(pady=5, fill="x", ipady=4)

        running = [False]
        # Button xử lý và đóng
        button_frame = tk.Frame(root, padx=10, pady=10)
        button_frame.pack(fill="x")

        process_button = tk.Button(button_frame, text="Xử lý", command=lambda: process_file(tk, logging_text, running, video_id, process_button), width=10)
        process_button.pack(side="left", padx=5, pady=10)

        pause_button = tk.Button(button_frame, text="Tạm dừng", command=lambda: stop_processing(running, process_button) , width=10)
        pause_button.pack(side="left", padx=100, pady=10)

        close_button = tk.Button(button_frame, text="Đóng", command=close_app, width=10)
        close_button.pack(side="right", padx=5, pady=10)

        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")