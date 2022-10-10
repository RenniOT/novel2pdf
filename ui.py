from tkinter import Tk, Label, Entry, Button, messagebox
import sys
from PIL import Image, ImageTk
import pyperclip
from main import load_shit
from time import sleep
import easygui
import imghdr

# please don't judge me 😭
global_variable = ""


class PdfUI:
    def __init__(self, novel_data):
        self.pdf_name = ""
        self.start = ""
        self.end = ""
        self.interval = ""

        self.chapter_count = novel_data.df.shape[0]
        self.image_loc = novel_data.cover
        self.novel_title = novel_data.title

        self.window = Tk()
        self.window.config(padx=20, pady=12)
        self.window.title(self.novel_title)

        self.main_label = Label(text="Please select pdf options:")

        self.name_label = Label(text="Name:")
        self.name_entry = Entry(width=30)

        self.start_label = Label(text="Starting chapter:")
        self.start_entry = Entry(width=15)

        self.end_label = Label(text="Ending chapter:")
        self.end_entry = Entry(width=15)

        self.interval_label = Label(text="Interval:")
        self.interval_entry = Entry(width=15)

        self.custom_image_button = Button(text="Custom Image", command=lambda: [self.import_image(), self.load_image()])
        self.image_file = self.image_loc[self.image_loc.rfind("/")+1:len(self.image_loc)]
        self.image_path_label = Label(text=self.image_file)
        self.generate_button = Button(text="Generate", command=lambda: [self.load_entries(), self.window.destroy()])
        self.exit_button = Button(text="Exit", command=self.window.destroy)

        # self.cover_canvas = Canvas(width=100, height=200)
        self.cover_image = ImageTk.PhotoImage(Image.open(self.image_loc).resize((193, 278)))
        self.image_label = Label(image=self.cover_image)

        self.generate_window()

        self.window.mainloop()

    def generate_window(self):
        self.main_label.grid(row=0, column=0, columnspan=4)

        self.name_label.grid(row=1, column=0)
        self.name_entry.grid(row=1, column=1, columnspan=3)
        self.name_entry.insert(0, self.novel_title)

        self.start_label.grid(row=2, column=0)
        self.start_entry.grid(row=2, column=1)
        self.start_entry.insert(0, "1")

        self.end_label.grid(row=2, column=2)
        self.end_entry.grid(row=2, column=3)
        self.end_entry.insert(0, str(self.chapter_count))

        self.interval_label.grid(row=3, column=1)
        self.interval_entry.grid(row=3, column=2)
        self.interval_entry.insert(0, "0")

        self.image_path_label.grid(row=5, column=0, columnspan=2)
        self.custom_image_button.grid(row=6, column=0, columnspan=2)
        self.generate_button.grid(row=7, column=0, columnspan=2)
        self.exit_button.grid(row=8, column=0, columnspan=2)

        self.image_label.grid(row=5, column=2, rowspan=4, columnspan=3)

    def load_image(self):
        self.cover_image = ImageTk.PhotoImage(Image.open(self.image_loc).resize((193, 278)))
        self.image_label.config(image=self.cover_image)
        self.image_label.grid(row=4, column=1, rowspan=4, columnspan=3)

    def import_image(self):
        is_valid_image = False
        while not is_valid_image:
            messagebox.showinfo(message="choose .png or .jpg for cover image...")
            sleep(.5)
            self.image_loc = easygui.fileopenbox()
            self.image_file = self.image_loc[self.image_loc.rfind("/") + 1:len(self.image_loc)]
            path_suffix = imghdr.what(self.image_loc)
            match path_suffix:
                case 'png':
                    is_valid_image = True
                case 'jpg':
                    is_valid_image = True
                case 'jpeg':
                    is_valid_image = True
                case _:
                    print(imghdr.what(self.image_loc))
                    pass
        self.image_path_label.config(text=self.image_file)

    def load_entries(self):
        self.pdf_name = self.name_entry.get()
        self.start = self.start_entry.get()
        self.end = self.end_entry.get()
        self.interval = self.interval_entry.get()

        if int(self.start) < 1 or self.start == "":
            self.start = 1
        else:
            self.start = int(self.start)
        if int(self.end) > self.chapter_count or self.end == "":
            self.end = self.chapter_count
        else:
            self.end = int(self.end)
        if self.end < self.start:
            self.end = self.start
        if int(self.interval) >= self.chapter_count or int(self.interval) < 1 or self.interval == "":
            self.interval = 0
        else:
            self.interval = int(self.interval)


def await_link():
    link_window = Tk()
    link_window.config(padx=15, pady=10)
    link_window.title("No link found")
    wait_for_link_message = Label(text='No link found, please copy a link from this website before clicking continue')
    wait_for_link_message.grid(column=0, row=0, columnspan=2)
    continue_button = Button(text='Continue', command=lambda: [link_window.destroy(), load_shit(pyperclip.paste())])
    continue_button.grid(column=0, row=1)
    exit_button = Button(text='Exit', command=sys.exit)
    exit_button.grid(column=1, row=1)
    link_window.mainloop()


def prompt_name(novel_name):
    name_window = Tk()
    name_window.config(padx=15, pady=10)
    name_window.title("Enter directory name")

    name_input_label = Label(text='Please enter a name for the new directory')
    name_input_label.grid(column=0, row=0, columnspan=2)
    name_entry = Entry(width=30)
    name_entry.insert(0, novel_name)
    name_entry.grid(column=0, row=1)
    confirm_button = Button(text='Confirm', command=lambda: [assign_return(name_entry.get()), name_window.destroy()])
    confirm_button.grid(column=1, row=1)

    name_window.mainloop()
    return global_variable


def yes_no(prompt):
    yes_no_window = Tk()
    yes_no_window.config(padx=15, pady=10)
    yes_no_window.title("Prompt window")

    prompt_label = Label(text=prompt)
    prompt_label.grid(column=0, row=0, columnspan=2)
    yes_button = Button(text="Yes", command=lambda: [assign_return(True), yes_no_window.destroy()])
    no_button = Button(text="No", command=lambda: [assign_return(False), yes_no_window.destroy()])
    yes_button.grid(column=0, row=1)
    no_button.grid(column=1, row=1)

    yes_no_window.mainloop()
    return global_variable


# trash garbage disgusting gross yucky eww function, I couldn't think of another way to do it, blame tkinter
def assign_return(value):
    global global_variable
    global_variable = value