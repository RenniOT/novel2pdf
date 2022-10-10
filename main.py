#!/usr/bin/env python3

from parse_chapter_data import ScrapeNovel
import webbrowser
from tkinter import messagebox
import os
import pyperclip
import easygui
import ui
import asyncio
from fpdf import FPDF


async def allocate_pdf(novel_data):
    ui_inputs = ui.PdfUI(novel_data)
    index_tuples = []
    interval = ui_inputs.interval
    start = ui_inputs.start
    end = ui_inputs.end
    if ui_inputs.interval != 0:
        action_count = (end - start) // interval
        for x in range(action_count - 1):
            index_tuples.append((x + start + interval * x - 1, start + interval * (x + 1) + x))
        index_tuples.append((action_count - 1 + start - 1 + interval * (action_count - 1), end))
    else:
        index_tuples.append((start - 1, end))
    return index_tuples, ui_inputs


async def generate_pdf(data, indices, name, cover, path, list_ch=True):
    file_name = [name + f"({indices[0] + 1}-{indices[1]})" + ".pdf" if list_ch is True else name + ".pdf"][0]
    output_path = os.path.join(path, file_name)
    doc_name = data.title
    titles = data.df["Title"].iloc[indices[0]:indices[1]]
    chapter_content = data.df["Content"].iloc[indices[0]:indices[1]]

    base_dejavu_path = 'dejavu'
    pdf = FPDF("P", "mm", "A3")
    pdf.set_margins(left=25.4, right=25.4, top=25.4)
    pdf.set_line_width(4)
    pdf.add_page()
    pdf.image(cover, 0, 0, w=297, h=420)
    pdf.add_font('DejaVu', '', os.path.join(base_dejavu_path, 'DejaVuSerif.ttf'))
    pdf.add_font('DejaVu', 'B', os.path.join(base_dejavu_path, 'DejaVuSerif-Bold.ttf'))

    pdf.add_page()
    pdf.set_font("DejaVu", "U", 30)
    pdf.write(txt=doc_name + "\n\n")
    pdf.set_font("DejaVu", "B", 20)
    pdf.write(txt="Table of contents:\n\n")
    pdf.set_font("DejaVu", "", 15)
    for title in titles:
        pdf.write(txt=f"{title}\n\n")

    for chapter in chapter_content:
        pdf.add_page()
        pdf.set_font("DejaVu", 'B', size=18)
        related_index = chapter_content[chapter_content == chapter].index[0]
        pdf.write(txt=f"{titles[related_index]}\n\n")
        pdf.set_font("DejaVu", '', size=14)
        for line in chapter.find_all("p"):
            pdf.write(txt=line.text + "\n\n")

    pdf.output(output_path)


async def handle_data(novel_data):
    messagebox.showinfo(title="Choose Directory", message="Please select the directory where you would like the "
                                                          "files to go")
    dir_loc = easygui.diropenbox()
    dir_name = ui.prompt_name(novel_data.title)
    file_path = os.path.join(dir_loc, dir_name)
    try:
        os.makedirs(file_path)
    except FileExistsError as f:
        print(f, "skipping file creation")
    finally:
        novel_data.dl_novel_cover(file_path)
    from_ui = await allocate_pdf(novel_data)
    index_tuples = from_ui[0]
    ui_inputs = from_ui[1]
    if len(index_tuples) == 1:
        await generate_pdf(data=novel_data, indices=index_tuples[0],
                           list_ch=ui.yes_no("List chapter numbers in file name?"), name=ui_inputs.pdf_name,
                           cover=ui_inputs.image_loc, path=file_path)
    else:
        tasks = []
        for index in index_tuples:
            tasks.append(asyncio.create_task(generate_pdf(data=novel_data, indices=index, name=ui_inputs.pdf_name,
                                                          cover=ui_inputs.image_loc, path=file_path)))
        for task in tasks:
            await task

    while ui.yes_no(prompt=f"Convert more from {novel_data.title}?"):
        await allocate_pdf(novel_data)


def load_shit(link):
    try:
        novel_data = ScrapeNovel(link)
    except Exception as exc:
        print('ignore if program continues to function - error:', exc)
        webbrowser.open('https://www.box-novel.com/', new=2)
        ui.await_link()
    else:
        asyncio.run(handle_data(novel_data))


if __name__ == '__main__':
    url = pyperclip.paste()
    load_shit(url)

