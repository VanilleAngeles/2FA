#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
2FA.py
Two Factors Authentifior
Use GTK+ Python3

Special thanks for https://github.com/CyrilleBiot in his advice, his help, his support
Rather than using pip for free modules, I preferred to integrate the source code by mentioning their authors:
- susam for mintotp.totp code https://github.com/susam/mintotp
- vasjip for python-gnupg https://github.com/vsajip/python-gnupg

Bibliography
  Gtk Reference Manual --> https://python-gtk-3-tutorial.readthedocs.io/en/latest/install.html
  os.environ --> https://www.delftstack.com/fr/howto/python/how-to-access-environment-variables-in-python/
  
Version
  V1 - intial
  V2 - use popover tecnology to add secondary menu in the header
"""
try:
	import gi,json, gnupg, os, shutil, datetime, configparser, sys, math, base64, hmac, struct, sys, time
except ModuleNotFoundError as e:
	print('[E] Module not installed', e)
	exit()
from os import path as os_path

try:
	gi.require_version('Gtk', '3.0')
except:
	print('[E] wrong Gtk version')
	exit()

try:
	from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio
except ModuleNotFoundError as e:
	print('[E] Module not installed', e)
	exit()
	
class MyApplication(Gtk.Window):

	def __init__(self):
		self.Read_Parameters()
		self.Password_Window()
		
##########################################
# READ INITIAL PARAMETERS
##########################################
	def Read_Parameters(self):
		# Change Directory to be on the same place than de current program
		Dir = os.path.dirname(__file__)
		if Dir != "":
			os.chdir(Dir)
		
		# we read INI file to locate files, directories and language
		Contener = configparser.ConfigParser()	
		if not os.path.exists('2FA.ini'): print('[E] No INI file'); exit()
		Contener.read('2FA.ini')
		
		self.PgpFiles = self.TranslateEnv(self,Contener['Directories']['PgpFiles'])
		self.IconFiles = self.TranslateEnv(self,Contener['Directories']['IconFiles'])
		self.SavedFiles = self.TranslateEnv(self,Contener['Directories']['SavedFiles'])
		self.JsonFile = self.TranslateEnv(self,Contener['Directories']['JsonFile'])
		CssFile = self.TranslateEnv(self,Contener['Directories']['CssFile'])
		self.ScrollWindowHeight = int(Contener['Values']['ScrollWindowHeight'])
		self.ScrollWindowWidth = int(Contener['Values']['ScrollWindowWidth'])
		self.JsonUpdated = False
		Langage = Contener['Values']['Lang']
		if Langage == 'Default':
			Langage = os.environ['LANG'][0:2]
		try:
			self.TextArray = Contener['Values'][Langage].split('|')
		except:
			self.TextArray = Contener['Values']['en'].split('|')
		
		#------ acces to CSS file
		style_provider = Gtk.CssProvider()
		style_provider.load_from_path(CssFile)
		Gtk.StyleContext.add_provider_for_screen(
		   Gdk.Screen.get_default(),
		  style_provider,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

##########################################
# DISPLAY PASSWORD WINDOW
##########################################
	def Password_Window(self):
		#------ Window created
		Gtk.Application.__init__(self)
		self.quit_selection = Gtk.ModelButton(label='Exit')
#		self.set_default_size(500, 500)
		self.set_resizable(False)
		self.set_border_width(10)
		
		#------ Header menu
		self.hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.hbox.add(self.quit_selection)
		self.quit_selection.connect('clicked', self.on_quit_clicked)
		self.hbox.show_all()
		
		self.popover = Gtk.Popover()
		self.popover.set_border_width(2)
		self.popover.add(self.hbox)
	
		menu_button = Gtk.MenuButton(popover=self.popover)
		menu_icon = Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.MENU)
		menu_icon.show()
		menu_button.add(menu_icon)
		menu_button.show()

		hbar = Gtk.HeaderBar()
		hbar.props.show_close_button = True
		hbar.props.title = '2FA'
		hbar.add(menu_button)
		hbar.show()
		self.set_titlebar(hbar)
		
		#------ Vertical box for inquiry password
		self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.add(self.vbox)
		
		Pixbuf1 = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=self.IconFiles + '2FAred.png', width=64, height=64, preserve_aspect_ratio=True)
		self.Image1 = Gtk.Image.new_from_pixbuf(Pixbuf1)
		self.vbox.pack_start(self.Image1, True, True, 0)
		
		self.Label1 = Gtk.Label()
		self.Label1.set_text(self.TextArray[0])
		self.vbox.pack_start(self.Label1, True, True, 0)

		Password = Gtk.Entry()
		Password.set_visibility(False)
		Password.connect('activate', self.Password_Validation)
		self.vbox.pack_start(Password, True, True, 0)

	def on_quit_clicked(self, widget):
		Gtk.main_quit()

	#------ Translate $HOME $CURRENT in expansive notation
	def TranslateEnv(self, User_Data, Directory):
		Result=Directory
		if Directory.find('$HOME') != -1:
			Result=Directory.replace('$HOME',os.environ['HOME'])
		if Directory.find('$CURRENT') != -1:
			Result=Directory.replace('$CURRENT',os_path.abspath(os_path.split(__file__)[0]))
		return(Result)
		
	#------ Password validation with pgp key
	def Password_Validation(self, entry):
		#------ Input password Entry
		self.Password = entry.get_text()

		#------ Check Password with PGP key
		Active_Path = os_path.abspath(os_path.split(__file__)[0]) + '/'
		Gpg_Directory = gnupg.GPG(gnupghome=self.PgpFiles)
		Crypted_File=open(self.JsonFile, 'rb')
		self.Json_File=Gpg_Directory.decrypt_file(Crypted_File, passphrase=self.Password)
		Crypted_File.close()
		self.Json_File=str(self.Json_File)

		#------ if right Password, the Json file is decrypted, else Error Message
		if self.Json_File == '':
			dialog = Gtk.MessageDialog (
				transient_for=self,
				flags=0,
				message_type=Gtk.MessageType.ERROR,
				buttons=Gtk.ButtonsType.CANCEL,
				text=self.TextArray[1])
			dialog.format_secondary_text(self.TextArray[2])
			dialog.run()
			dialog.destroy()
			return()
		else:
			self.Json_File = eval(self.Json_File)
			self.First=True
			self.Display_Codes()

##########################################
# DISPLAY CODES
##########################################
	def Display_Codes(self):
		#------ Clear window
		Elements = self.hbox.get_children()
		for Element in Elements:
			self.hbox.remove (Element)
		Elements = self.vbox.get_children()
		for Element in Elements:
			self.vbox.remove (Element)
		#------ modify header menu
		self.add_selection = Gtk.ModelButton(label="Add")
		self.delete_selection = Gtk.ModelButton(label="Delete")
		self.save_selection = Gtk.ModelButton(label="Save")
		self.restore_selection = Gtk.ModelButton(label="Restore")
		self.help_selection = Gtk.ModelButton(label="Help")
		self.about_selection = Gtk.ModelButton(label="About")
		self.quit_selection = Gtk.ModelButton(label="Exit")
		
		self.hbox.add(self.add_selection)
		self.add_selection.set_sensitive(True)
		self.add_selection.connect('clicked', self.on_add_clicked)

		self.hbox.add(self.delete_selection)
		self.delete_selection.set_sensitive(False)
#		self.delete_selection.connect('clicked', self.on_delete_clicked)

		self.hbox.add(self.save_selection)
		self.save_selection.set_sensitive(False)
		self.save_selection.connect('clicked', self.on_save_clicked)

		self.hbox.add(self.restore_selection)
		self.restore_selection.set_sensitive(True)
		self.restore_selection.connect('clicked', self.on_restore_clicked)

		self.hbox.add(self.help_selection)
		self.help_selection.set_sensitive(True)
		self.help_selection.connect('clicked', self.on_help_clicked)

		self.hbox.add(self.about_selection)
		self.about_selection.set_sensitive(True)
		self.about_selection.connect('clicked', self.on_about_clicked)

		self.hbox.add(self.quit_selection)
		self.quit_selection.set_sensitive(True)
		self.quit_selection.connect('clicked', self.on_quit_clicked)

		self.hbox.show_all()

		#------ Main logo
		Pixbuf2 = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=self.IconFiles + '2FA.png', width=64, height=64, preserve_aspect_ratio=True)
		self.Image1 = Gtk.Image.new_from_pixbuf(Pixbuf2)
		self.vbox.pack_start(self.Image1, True, True, 0)

		#------ Display Codes & Progress Bar (the progress bar must start à 0" ou 30" realtime
		self.ProgressBar = Gtk.ProgressBar()
		Second=datetime.datetime.now().second
		if Second > 30:
			Second = Second - 30
		Fraction = 1 / 30 * Second
		self.ProgressBar.set_fraction(Fraction)
		self.vbox.pack_start(self.ProgressBar, True, True, 0)
		
		#------ Activate Save button if necessary
		if self.JsonUpdated:
			self.save_selection.set_sensitive(True)

		#------ GRID
		self.grid = Gtk.Grid()
		self.grid.set_hexpand(True)
		self.grid.set_column_spacing(10)
		
		PixbufCopy = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=self.IconFiles + "copy.png", width=16, height=16, preserve_aspect_ratio=True)
		PixbufDelete = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=self.IconFiles + "delete.png", width=32, height=32, preserve_aspect_ratio=True)
		PixbufInformation = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=self.IconFiles + "information.png", width=16, height=16, preserve_aspect_ratio=True)
		
		# Init, specially Key Table for easy delete
		self.Keys_List=''
		self.Keys_List = list(self.Keys_List)
		I = 0	# the GUI line
		J = 0	# the table index
		
		# Build the grid for each record in Json File
		for Keys in self.Json_File.keys():
			self.Keys_List.append(Keys)
			Record = Keys.split('*')
			WebSite = Record[0]
			Username = Record[1]
			Base32Key=self.Json_File.get(Keys)
			NumericCode = self.totp(Base32Key)
			
			WebSiteLogoName=self.IconFiles + str(WebSite).lower() + '.png'
			if os.path.isfile(WebSiteLogoName):
				Pixbuf2 = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=WebSiteLogoName, width=32, height=32, preserve_aspect_ratio=True)
				self.Unknown = Gtk.Image.new_from_pixbuf(Pixbuf2)
			else:
				WebSiteLetter = WebSite[0]
				self.Unknown = Gtk.Label(label=WebSiteLetter)
			
			self.Label3 = Gtk.Label(label=WebSite)
			self.Label3.set_name('WebSite')

			self.Label4 = Gtk.Label(label=Username)
			self.Label4.set_name('Username')

			self.Button2 = Gtk.Button(label=NumericCode)
			self.Button2.set_name('NumericCode')
			self.Button2.connect('clicked', self.CopyToClipboard, NumericCode)

			self.Button4 = Gtk.Button()
			Icone = Gtk.Image.new_from_pixbuf(PixbufDelete)
			self.Button4.set_image(Icone)
			self.Button4.connect('clicked', self.Delete_Entry, J, WebSite, Username)

			self.grid.attach(self.Unknown, 0, I, 1, 2)
			self.grid.attach(self.Label3, 1, I, 1, 1)
			self.grid.attach(self.Label4, 1, I+1, 1, 1)
			self.grid.attach(self.Button2, 2, I, 1, 2)
			self.grid.attach(self.Button4, 3, I, 1, 2)
			self.vbox.show_all()
			I += 2
			J += 1
		
		# grid in a scrolled area
		ScrolledWindow = Gtk.ScrolledWindow()
		ScrolledWindow.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
		ScrolledWindow.set_min_content_height(self.ScrollWindowHeight)
		ScrolledWindow.set_min_content_width(self.ScrollWindowWidth)
		ScrolledWindow.add(self.grid)
		self.vbox.add(ScrolledWindow)
		self.vbox.show_all()

		# if first time, start the timeout ProgressBarr
		if self.First:
			self.timeout_id = GLib.timeout_add(100, self.on_timeout, None)
			self.First = False


##########################################
# PROCEDURES FOR HEADER MENU
##########################################
	#------ Applications Menu ABOUT
	def on_about_clicked (self, widget):
		dialog = Gtk.MessageDialog(
			transient_for=self,
			flags=0,
			message_type=Gtk.MessageType.INFO,
			buttons=Gtk.ButtonsType.OK,
			text="2FA")
		Dialog_Details = '2FA.py \n' +	\
		'Utility for store double factor authentification codes\n' + \
		'Coded with GUI Gtk3\n' + \
		'__author & credits & maintainer & email__ \n PatrickConstant <patrick@constant.onl>\n' + \
		'__copyright__ Copyleft\n' + \
		'__credits__ Vangeles <vanille.angeles@gmail.com>\n' + \
		'__license__ GPL\n' + \
		'__version__ 0.1\n' + \
		'__date__ 2020/12/05\n' + \
		'__status__ Devel'

		dialog.format_secondary_text(Dialog_Details)
		dialog.run()
		dialog.destroy()

	#------ Applications Menu HELP
	def on_help_clicked (self, widget):
		dialog = Gtk.MessageDialog(
			transient_for=self,
			flags=0,
			message_type=Gtk.MessageType.INFO,
			buttons=Gtk.ButtonsType.OK,
			text="2FA")
		Dialog_Details = '2FA.py \n' +	\
		'> 2FA.ini contains intial parameters\n' + \
		'> The activity barr is a standard 30" length\n ' + \
		'> You can copy Codes to clipboard by clicking on Code or associated copy icon\n' + \
		'> The Delete action remove from active data (in memory), not form the crypted database\n' + \
		'> To add a 2FA code, the Mnemonic, the user and the given key are necessary\n' + \
		'> If you want a icon (not a simple caracters, you need to put a png (lowercase) file in Pictures directory (cf 2FA.ini) \n' + \
		'> To store modifications in databae (add or delete), you must save the data\n' + \
		'> If the changes are saved, the previous crypted file is store in Data directory with date/hour extension (cf 2FA.ini\n' + \
		'Enjoy'

		dialog.format_secondary_text(Dialog_Details)
		dialog.run()
		dialog.destroy()
	#------ Application menu  SAVE
	def on_save_clicked (self, widget):
		if not self.JsonUpdated:
			return()
		JsonVersion = str(datetime.datetime.now().time())
		SavedFile = self.SavedFiles + JsonVersion
		shutil.copy(self.JsonFile, SavedFile)
		with open(self.SavedFiles + 'toptp.json' , 'w') as FileName:
			Status = FileName.write(json.dumps(self.Json_File, indent=4))
		FileName.close()
		with open(self.SavedFiles + 'toptp.json', 'rb') as FileName:
			CryptedFile = gnupg.GPG(gnupghome=self.PgpFiles)
			Status = CryptedFile.encrypt_file(FileName, symmetric='AES256', recipients=None, output=self.JsonFile, passphrase=self.Password)
		FileName.close()
		os.remove(self.SavedFiles + 'toptp.json')
		self.JsonUpdates = False
		dialog = Gtk.MessageDialog (
			transient_for=self,
			flags=0,
			message_type=Gtk.MessageType.INFO,
			buttons=Gtk.ButtonsType.OK,
			text=self.TextArray[5])
		dialog.format_secondary_text(self.TextArray[6] + '\n' + SavedFile)
		dialog.run()
		dialog.destroy()
		return()

	#------ Application menu ADD
	def on_add_clicked (self, widget):
		# Create a new screen
		Add_Window = Gtk.Window(title=self.TextArray[7])
		Add_Window.connect("destroy", self.Exit_Window, Add_Window)
		Add_Window.show_all()
		Add_Window.set_default_size(200, 200)
		Add_Window.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		Add_Window.add(Add_Window.vbox)
		# Input fields
		LabelSite = Gtk.Label(label=self.TextArray[8])
		Add_Window.vbox.pack_start(LabelSite, True, True, 0)
		EntrySite = Gtk.Entry()
		Add_Window.vbox.pack_start(EntrySite, True, True, 0)

		LabelUser = Gtk.Label(label=self.TextArray[9])
		Add_Window.vbox.pack_start(LabelUser, True, True, 0)
		EntryUser = Gtk.Entry()
		Add_Window.vbox.pack_start(EntryUser, True, True, 0)

		LabelKey = Gtk.Label(label=self.TextArray[10])
		Add_Window.vbox.pack_start(LabelKey, True, True, 0)
		EntryKey = Gtk.Entry()
		Add_Window.vbox.pack_start(EntryKey, True, True, 0)

		GenerateButton = Gtk.Button(label=self.TextArray[11])
		GenerateButton.connect('clicked', self.GenerateRecord, EntrySite, EntryUser, EntryKey)
		Add_Window.vbox.pack_start(GenerateButton, True, True, 0)

		ExitButton = Gtk.Button(label=self.TextArray[12])
		ExitButton.connect('clicked',  self.Exit_Window, Add_Window)
		Add_Window.vbox.pack_start(ExitButton, True, True, 0)

		Add_Window.show_all()
	
	#------ Reset Progress bar
	def on_timeout(self, user_data):
		self.ProgressBar.pulse() 
		new_value = self.ProgressBar.get_fraction() + 0.00333
		if new_value > 1:
			new_value = 0
			self.Display_Codes()
		self.ProgressBar.set_fraction(new_value)
		return True
	
	#------ Copy code to clipboard
	def CopyToClipboard(self, usre_data, Param):
		Clipboard=Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		Clipboard.set_text(Param, -1)
		Clipboard.store()

	#------ Delete JSON record from volatile memory
	def Delete_Entry(self, user_data, I, WebSite, Username):
		MessageDialog = Gtk.MessageDialog(parent=self, 
			modal=True, 
			message_type=Gtk.MessageType.WARNING, 
			buttons=Gtk.ButtonsType.OK_CANCEL, 
			text=self.TextArray[3])
		Text_Details = self.TextArray[3] + '\n' + WebSite + '\n' + self.TextArray[4] + '\n' + Username
		MessageDialog.format_secondary_text(Text_Details)
		MessageDialog.connect('response', self.dialog_response, I)
		MessageDialog.show()
		
		
	def dialog_response(self, widget, response_id, I):
		if response_id == Gtk.ResponseType.OK:
			self.JsonUpdated = True
			del self.Json_File[self.Keys_List[I]]
		widget.destroy()
		self.Display_Codes()
	

	#------ close the specific window
	def Exit_Window(self, User_Data, window):
		window.hide()
		return True

	#------ check entries & generate the record
	def GenerateRecord(self, entry, EntrySite, EntryUser, EntryKey ):
		SiteRecord = EntrySite.get_text().replace(' ','')
		UserRecord = EntryUser.get_text().replace(' ','')
		KeyRecord = EntryKey.get_text().replace(' ','')
		try:
			GeneratedCode=self.totp(KeyRecord)
		except:
			GeneratedCode=''
		if GeneratedCode == '':
			dialog = Gtk.MessageDialog (
				transient_for=self,
				flags=0,
				message_type=Gtk.MessageType.ERROR,
				buttons=Gtk.ButtonsType.CANCEL,
				text=self.TextArray[13])
			dialog.format_secondary_text(self.TextArray[14])
			dialog.run()
			dialog.destroy()
		else:
			JsonRecord = SiteRecord + '*' + UserRecord
			self.Json_File[JsonRecord]=KeyRecord
			self.JsonUpdated = True
			self.Display_Codes()
			return()

	#------ Application menu RESTORE
	def on_restore_clicked (self, widget):
		# Input fields...
		FileChooserDialog = Gtk.FileChooserDialog(title=self.TextArray[15],action=Gtk.FileChooserAction.OPEN)
		FileChooserDialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
		# ...in the backup Folder...
		FileChooserDialog.set_current_folder(self.SavedFiles)
		# ... only for txt files
		filter_text = Gtk.FileFilter()
		filter_text.set_name("Text files")
		filter_text.add_mime_type("text/plain")
		FileChooserDialog.add_filter(filter_text)
		# Response analysis
		FileChoosed = FileChooserDialog.run()
		if FileChoosed == Gtk.ResponseType.OK:
			ChoosedFile = FileChooserDialog.get_filename()
		else:
			FileChooserDialog.destroy()
			return()
		MessageDialog = Gtk.MessageDialog(parent=self, 
			modal=True, 
			message_type=Gtk.MessageType.WARNING, 
			buttons=Gtk.ButtonsType.OK_CANCEL, 
			text=self.TextArray[16])
		Text_Details = self.TextArray[17] + '\n' + self.JsonFile + '\n' + self.TextArray[18] +'\n' + ChoosedFile
		MessageDialog.format_secondary_text(Text_Details)
		MessageDialog.connect('response', self.Restore_Response, ChoosedFile)
		MessageDialog.show()
		FileChooserDialog.destroy()
		return()

	def Restore_Response(self, widget, response_id, ChoosedFile):
		if response_id == Gtk.ResponseType.OK:
			shutil.copy(ChoosedFile, self.JsonFile)
			dialog = Gtk.MessageDialog (
				transient_for=self,
				flags=0,
				message_type=Gtk.MessageType.INFO,
				buttons=Gtk.ButtonsType.OK,
				text=self.TextArray[19])
			dialog.format_secondary_text(self.TextArray[20])
			dialog.run()
			dialog.destroy()
		widget.destroy()

	#------ Code from https://github.com/susam/mintotp
	def hotp(self, key, counter, digits=6, digest='sha1'):
		key = base64.b32decode(key.upper() + '=' * ((8 - len(key)) % 8))
		counter = struct.pack('>Q', counter)
		mac = hmac.new(key, counter, digest).digest()
		offset = mac[-1] & 0x0f
		binary = struct.unpack('>L', mac[offset:offset+4])[0] & 0x7fffffff
		return str(binary)[-digits:].rjust(digits, '0')


	def totp(self, key, time_step=30, digits=6, digest='sha1'):
		return self.hotp(key, int(time.time() / time_step), digits, digest)

			
#----- Init
win = MyApplication()
win.connect("destroy", Gtk.main_quit)
win.set_default_size(width=250, height=100)
win.show_all()
Gtk.main()
