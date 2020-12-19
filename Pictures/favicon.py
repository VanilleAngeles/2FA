#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request
from tkinter import *
from PIL import Image

def Init_Page():
	global WS, WI
	Clear_Win()
	WP.geometry("200x300")
	Label(WP,text='Nom de l\'icone', font=("Courier",12,"bold"), width=20).pack()
	WI=Entry(WP,width=20)
	WI.pack()
	Label(WP,text='URL du site', font=("Courier",12,"bold"), width=20).pack()
	WS=Entry(WP,width=20)
	WS.pack()
	WS.bind('<Return>', (lambda event: Favicon()))
	WS.pack()
#	Site.focus_force()
	BE=Button(WP, text='Exit', font=("Courier",12,"bold"), overrelief='raised', borderwidth=3, command=WP.quit, width=5, height=1)
	BE.pack()


def Favicon():
	global Icone
	Site=WS.get()
	Site=str(Site)
	Site=Site+'/favicon.ico'
	Icone=WI.get()
	if Icone == '':
		return
	else:
		FI=Icone+'.ico'
		FP=Icone+'.png'
	try:
		ICO = urllib.request.urlopen(Site)
		source=ICO.read()
		FILE=open(FI,'wb')
		FILE.write(source)
		FILE.close()
	except:
		FI='null.ico'
	
	try:
		IMG=Image.open(FI)
	except:
		IMG=Image.open('null.ico')
	size=32,32
	IMG.thumbnail(size,Image.ANTIALIAS)
	IMG.save(FP, format='PNG')
	
	Clear_Win()
	Icone=PhotoImage(file=FP)
	Button(WP, image=Icone, height=32, width=32).pack()
	BE=Button(WP, text='Exit', font=("Courier",12,"bold"), overrelief='raised', borderwidth=3, command=WP.quit, width=5, height=1)
	BE.pack()
	BR=Button(WP, text='Return', font=("Courier",12,"bold"), overrelief='raised', borderwidth=3, command=lambda : Init_Page(), width=5, height=1)
	BR.pack()

# Reset the page
def Clear_Win():
	for c in WP.winfo_children():
		c.destroy()

WP=Tk()
WP.title('Favicon')

Init_Page()

WP.mainloop()
