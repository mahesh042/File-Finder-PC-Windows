import tkinter as tk
import tkinter.font as tkfont
import os,ctypes,win32api,customtkinter
import concurrent.futures

customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("blue")
script_directory = os.path.dirname(os.path.abspath(__file__))


root = customtkinter.CTk()
root.title("File Finder")
root.geometry("700x450")

myappid = 'mycompany.myproduct.subproduct.version'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

file_name_var = tk.StringVar()

def find_in_drive(drive, file_name):
    result = []
    for root, _, files in os.walk(drive):
        for file in files:
            if file_name.lower() in file.lower():
                result.append(os.path.join(root, file))
    return result

def find_in_all_drives():
    drives = [drive for drive in win32api.GetLogicalDriveStrings().split('\000')[:-1] if drive.lower() != 'c:\\']
    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(find_in_drive, drive, file_name_var.get()) for drive in drives]

        for future in concurrent.futures.as_completed(futures):
            results.extend(future.result())

    root.after(0, update_results, results)
    

def update_results(results):
    results_text = ""
    results_box.config(state=tk.NORMAL)
    results_box.delete("1.0", tk.END)

    font_family = "Helvetica"
    font = tkfont.Font(family=font_family, size=12)

    if not results:
        results_box.insert(tk.END, "No matching files found.")
    else:
        for result in results:
            result = result.strip()
            frame = tk.Frame(results_box, bd=1, relief="solid", bg="#F0F0F0")

            open_button = tk.Label(frame, text="Open File", bg="#4682B4", fg="#FFFFFF", padx=5, pady=2, cursor="hand2", justify=tk.CENTER, font=font)
            open_button.pack(side=tk.LEFT)
            open_button.bind("<Button-1>", lambda event, path=result: open_file(path))

            open_location_button = tk.Label(frame, text="Open File Location", bg="#2E8B57", fg="#FFFFFF", padx=5, pady=2, cursor="hand2", justify=tk.CENTER, font=font)
            open_location_button.pack(side=tk.LEFT)
            open_location_button.bind("<Button-1>", lambda event, path=result: open_file_location(path))

            path_label = tk.Label(frame, text=result, bg="#F0F0F0", fg="#000000", padx=5, pady=2, anchor="w", justify=tk.LEFT, font=font)
            path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            results_box.window_create(tk.END, window=frame)
            results_box.insert(tk.END, "\n")

    results_box.config(state=tk.DISABLED)

        

def open_file_location(file_path):
    os.system(f'explorer /select,"{file_path}"')

def open_file(file_path):
    os.startfile(file_path)

font_family = "Helvetica"
font = tkfont.Font(family=font_family, size=12)

input_frame = customtkinter.CTkFrame(master=root)
input_frame.pack(pady=20, padx=20, fill="both", expand=True)

file_name_entry = customtkinter.CTkEntry(master=input_frame, placeholder_text="Enter file name", textvariable=file_name_var)
file_name_entry.pack(pady=10, padx=10)

search_button = customtkinter.CTkButton(master=input_frame, text="Search", command=find_in_all_drives)
search_button.pack(pady=10, padx=10)

results_frame = customtkinter.CTkFrame(master=root)
results_frame.pack(pady=20, padx=20, fill="both", expand=True)

scrollbar_y = tk.Scrollbar(results_frame)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

scrollbar_x = tk.Scrollbar(results_frame, orient=tk.HORIZONTAL)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

results_box = tk.Text(master=results_frame, width=250, wrap=tk.WORD, bg="#F0F0F0", fg="#000000", yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
results_box.pack(pady=10, padx=10, fill="both", expand=True)
results_box.tag_configure("center", justify='center')
results_box.tag_add("center", "1.0", "end")

results_box.tag_bind("file_path", "<Button-1>", open_file)

scrollbar_y.config(command=results_box.yview)
scrollbar_x.config(command=results_box.xview)

root.mainloop()