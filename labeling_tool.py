import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pandas as pd
import requests
from io import BytesIO
import json
from functools import partial
from datetime import datetime


class ImageLabelingApp:
    def __init__(self, master, csv_file, classes_file):
        self.master = master
        self.csv_file = csv_file
        self.classes_file = classes_file
        self.df = pd.read_csv(csv_file)
        if 'Label' not in self.df.columns:
            self.df['Label'] = None
        self.current_index = 0
        self.current_label = None
        self.load_classes()
        self.create_widgets()
        self.current_index = self.get_first_unlabeled_index()
        self.display_image()

    def get_first_unlabeled_index(self):
        unlabeled_rows = self.df[self.df['Label'].isna()]
        if not unlabeled_rows.empty:
            return unlabeled_rows.index[0]
        else:
            return 0
        
    def load_classes(self):
        try:
            with open(self.classes_file, 'r') as f:
                self.label_classes = json.load(f)
        except FileNotFoundError:
            self.label_classes = []
        self.buttons = {}

    def create_widgets(self):
        self.panel_frame = tk.Frame(self.master, bg='white', bd=2, relief='sunken')
        self.panel_frame.pack(side="top", fill="both", expand="yes", padx=10, pady=10)

        self.navigation_frame = tk.Frame(self.master)
        self.navigation_frame.pack(side="bottom", fill="x", pady=(5, 10))

        self.panel = tk.Label(self.panel_frame)
        self.panel.pack(side="top", fill="both", expand="yes")
        
        self.info_frame = tk.Frame(self.master, bg='white')
        self.info_frame.pack(side="top", fill="x", pady=5)
        
        self.image_info_label = tk.Label(self.master, text="Image 1 of 10", font=('Helvetica', 14))
        self.image_info_label.pack(side="top", pady=(0, 10))

        self.control_frame = tk.Frame(self.master)
        self.control_frame.pack(side="top", fill="x", pady=5)
        
        self.selected_label_frame = tk.Frame(self.control_frame, bg=self.master.cget('bg'))
        self.selected_label_frame.pack(side="right", fill="x", expand=True)

        self.current_label_display = tk.Label(self.selected_label_frame, text="Selected Label: None", font=('Helvetica', 14))
        self.current_label_display.pack(side="left", padx=10)

        self.remove_class_button = tk.Button(self.selected_label_frame, text="Remove Selected Label", command=self.remove_selected_class, font=('Helvetica', 14))
        self.remove_class_button.pack(side="right", padx=10)

        self.new_class_entry = tk.Entry(self.control_frame, font=('Helvetica', 14))
        self.new_class_entry.pack(side="left", padx=10)
        
        self.add_label_button = tk.Button(self.control_frame, text="Add Label", command=self.add_and_label_new_class, font=('Helvetica', 14))
        self.add_label_button.pack(side="left", padx=10)
        
        self.save_button = tk.Button(self.navigation_frame, text="Save & Next", command=self.save_label_and_next, bg='#4CAF50', fg='black', font=('Helvetica', 14, 'bold'))
        self.save_button.pack(side="bottom", pady=(0, 20))

        self.prev_button = tk.Button(self.navigation_frame, text="Previous", command=self.prev_image, font=('Helvetica', 14))
        self.prev_button.pack(side="left", padx=10)

        self.next_button = tk.Button(self.navigation_frame, text="Next", command=self.next_image, font=('Helvetica', 14))
        self.next_button.pack(side="right", padx=10)

        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(side="top", fill="x", expand=True)

        self.master.bind("<Left>", self.prev_image)
        self.master.bind("<Right>", self.next_image)
        self.master.bind("<Return>", self.on_enter_pressed)

        for index, label_class in enumerate(self.label_classes, start=1):
            self.add_class_button(label_class, index)
            
    def next_image(self, event=None):
        if self.current_index < len(self.df) - 1:
            self.current_index += 1
            self.display_image()
            self.load_current_label()
        else:
            messagebox.showinfo("알림", "마지막 이미지입니다.")
            
    def prev_image(self, event=None):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_image()
            self.load_current_label()

    
    def load_current_label(self):
        current_label = self.df.at[self.current_index, 'Label']
        if pd.isna(current_label):
            display_label = 'None'
            self.current_label_display.config(fg='red')
        else:
            display_label = current_label
            self.current_label_display.config(fg='black')
        
        self.current_label_display.config(text=f"Selected Label: {display_label}")
        self.update_button_colors()       

            
    def display_image(self):
        if self.current_index < len(self.df):
            img_url = self.df.iloc[self.current_index]['URL']
            img = Image.open(BytesIO(requests.get(img_url).content))
            img = img.resize((400, 400), Image.ANTIALIAS)
            self.img = ImageTk.PhotoImage(img)
            self.panel.configure(image=self.img)
            self.update_button_colors()
            image_info_text = f"Image {self.current_index + 1} of {len(self.df)}"
            self.image_info_label.config(text=image_info_text)

            self.load_current_label()


    def set_current_label(self, class_name, event=None):
        self.current_label = class_name
        self.update_button_colors()
        label_text = f"Selected Label: {class_name if class_name else 'None'}"
        label_color = 'red' if class_name is None else 'black'
        self.current_label_display.config(text=label_text, fg=label_color)
  

    def save_label_and_next(self):
        if self.current_label:
            self.df.at[self.current_index, 'Label'] = self.current_label
            self.df.at[self.current_index, 'Last Modified Time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.df.to_csv(self.csv_file, index=False)
            self.current_index += 1
            self.current_label = None
            if self.current_index < len(self.df):
                self.display_image()
            else:
                messagebox.showinfo("완료", "모든 이미지가 라벨링되었습니다.")
                self.master.quit()
        else:
            messagebox.showwarning("경고", "라벨이 선택되지 않았습니다. 라벨을 선택하고 다시 시도하세요.")

    def remove_selected_class(self):
        if self.current_label and self.current_label in self.label_classes:
            if messagebox.askyesno("Remove Label", f"'{self.current_label}' 레이블을 제거하시겠습니까?"):
                self.label_classes.remove(self.current_label)
                with open(self.classes_file, 'w') as f:
                    json.dump(self.label_classes, f)

                self.recreate_buttons()
                self.current_label = None
                self.current_label_display.config(text="Selected Label: None", fg='black')
        else:
            messagebox.showerror("Error", "선택된 라벨이 리스트에 없습니다.")

    def recreate_buttons(self):
        for button in self.buttons.values():
           button.destroy()
        self.buttons.clear()
        for index, label_class in enumerate(self.label_classes, start=1):
            self.add_class_button(label_class, index)

    def add_class_button(self, class_name, index):
        shortcut_keys = '123456789qwertyuiop'
        shortcut_key = shortcut_keys[index - 1] if index <= len(shortcut_keys) else ''
        button_text = f"{shortcut_key}. {class_name}" if shortcut_key else class_name
        
        action = partial(self.set_current_label, class_name)
        button = tk.Button(self.button_frame, text=button_text, command=action, font=('Helvetica', 14))
        
        row = (index - 1) // 5
        column = (index - 1) % 5
        button.grid(row=row, column=column, sticky='nsew', padx=5, pady=5)
        self.buttons[class_name] = button
        
        if shortcut_key:
            self.master.bind(f"<KeyPress-{shortcut_key}>", lambda event, name=class_name: self.set_current_label(name))

    def on_enter_pressed(self, event=None):
        if self.new_class_entry.focus_get() == self.new_class_entry:
            self.add_and_label_new_class()
        else:
            self.save_label_and_next()
                
    def add_and_label_new_class(self):
        new_class = self.new_class_entry.get()
        if new_class and new_class not in self.label_classes:
            self.label_classes.append(new_class)
            with open(self.classes_file, 'w') as f:
                json.dump(self.label_classes, f)
            self.add_class_button(new_class, len(self.label_classes))
            self.set_current_label(new_class)
            self.new_class_entry.delete(0, tk.END)
            self.save_button.focus_set()


    def update_button_colors(self):
        for class_name, button in self.buttons.items():
            if class_name == self.current_label:
                button.config(bg='lightblue')
            else:
                button.config(bg='SystemButtonFace')

                

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Labeling Tool")
    app = ImageLabelingApp(root, 'image_urls.csv', 'label_classes.json')
    root.mainloop()
