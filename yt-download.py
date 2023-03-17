import tkinter as tk
#from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import END, messagebox
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from datetime import timedelta
from threading import Thread
import subprocess
import os


def insert_timestamp():

	try:
		url = link_entry.get()
		yt = YouTube(url)
		second_length = yt.length
		timestamp = timedelta(seconds=second_length)
		start_entry.insert(0,"0:00:00")
		end_entry.insert(0,timestamp)
	except RegexMatchError:
		messagebox.showerror('','Link problem')

	return

def cancel_link():

	link_entry.delete(0,END)
	start_entry.delete(0,END)
	end_entry.delete(0,END)

	return

def convert_to_seconds(time_str):

	hh,mm,ss=time_str.split(':')
	dt = hh+'H'+mm+'M'+ss+'S'
	return dt

def schedule_check(t):
    root.after(100, check_if_done, t)

def check_if_done(t):
    if not t.is_alive():
        down_label["text"] = "CLICK TO DOWNLOAD"
        down["state"] = "normal"
    else:
        schedule_check(t)

def progress_download(file_name):
    	
	url = link_entry.get()
	start_date = start_entry.get()
	end_date = end_entry.get()

	start_sec = convert_to_seconds(start_date)
	end_sec = convert_to_seconds(end_date)

	yt = YouTube(url)
	max_length = timedelta(seconds=yt.length)

	down_label["text"] = "DOWNLOADING..."
	down["state"] = "disabled"

	if opt.get() == "mp4":
		download_task_mp4 = subprocess.run(f'yt-dlp -S res,ext:mp4:m4a --recode mp4 -o "{file_name}.mp4" {url}')
		if end_date == str(max_length):
			messagebox.showinfo('Download completed', 'The mp4 file has been downloaded')
		else:
			cut_task_mp4 = subprocess.run(f'ffmpeg -i "{file_name}.mp4" -ss {start_date} -to {end_date} -c:v libx264 -crf 30 "{file_name}_part_{start_sec}_{end_sec}.mp4"')
			messagebox.showinfo('Download completed', 'The mp4 file has been downloaded')
	else:
		download_task_mp3 = subprocess.run(f'yt-dlp --extract-audio --audio-format mp3 --audio-quality=320k -o "{file_name}.mp3" "{url}"')
		if end_date == str(max_length):
			messagebox.showinfo('Download completed', 'The mp3 file has been downloaded')
		else:
			cut_task_mp3 = subprocess.run(f'ffmpeg -i "{file_name}.mp3" -ss {start_date} -to {end_date} "{file_name}_part_{start_sec}_{end_sec}.mp3"')
			messagebox.showinfo('Download completed', 'The mp3 file has been downloaded')



def download():
    	
	url = link_entry.get()
	start_date = start_entry.get()
	end_date = end_entry.get()
	correct_format_str = "0123456789:"

	if len(start_date)==0 or len(end_date)==0:
		messagebox.showwarning('','Please specify a start time and/or an end time')
	elif len(start_date)!=7 or len(end_date)!=7:
		messagebox.showwarning('','Times in wrong format. Please use H:MM:SS format.')
	elif not all(ch in correct_format_str for ch in start_date) or not all(ch in correct_format_str for ch in end_date):
		messagebox.showwarning('','Incorrect character in start and/or end time')
	else:
		start_sec = convert_to_seconds(start_date)
		end_sec = convert_to_seconds(end_date)
		file_name = subprocess.getoutput(f'yt-dlp --print filename --windows-filenames -o "%(title)s" {url}')
		if os.path.exists(f'{file_name}_part_{start_sec}_{end_sec}.mp4'):
			messagebox.showwarning('','The file exists already')
		else:
			t = Thread(target=progress_download, args=[file_name])
			t.start()
			schedule_check(t)
			

	return


root= ttk.Window(themename="darkly")
root.title('YouTube download')
#root.resizable(False,False)

link_frame = ttk.Frame(root)
link_frame.pack(pady=30)

link =ttk.Label(link_frame,text='LINK')
link.grid(row=2,column=0)

link_entry = ttk.Entry(link_frame, width=50)
link_entry.grid(row=3,column=0)

Input_frame = ttk.Frame(root)
Input_frame.pack(pady=30)

start = ttk.Label(Input_frame,text='START')
start.grid(row=5,column=0)

end = ttk.Label(Input_frame,text='END')
end.grid(row=5,column=1)

start_entry = ttk.Entry(Input_frame, width=25)
start_entry.grid(row=6,column=0,padx=50)

end_entry = ttk.Entry(Input_frame, width=25)
end_entry.grid(row=6,column=1,padx=50)

ok = ttk.Button(link_frame,text='OK',command=insert_timestamp)
ok.grid(row=3,column=1,padx=10)

dele = ttk.Button(link_frame,text='CANCEL',command=cancel_link)
dele.grid(row=3,column=2,padx=10)

down_frame = ttk.Frame(root)
down_frame.pack(pady=40)

down_label = ttk.Label(down_frame,text='CLICK TO DOWNLOAD')
down_label.grid(row=2,column=1,pady=10)

down = ttk.Button(down_frame,text='DOWNLOAD',width=35,command=download)
down.grid(row=3,column=1,padx=20)

list_opt = ["mp4","mp3"]
opt = tk.StringVar()

select = ttk.Combobox(down_frame,values=list_opt, textvariable=opt)
select.current(0)
select["state"] = "readonly"
select.grid(row=3,column=0,padx=10)


root.mainloop()
	

