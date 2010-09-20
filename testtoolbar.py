#encoding: utf-8
import gtk, os

from urllib import urlretrieve
from lxml import etree

from sugar.graphics.toolbutton import ToolButton

class TestToolbar(gtk.Toolbar):

    def __init__(self, handle):
        gtk.Toolbar.__init__(self)
        self.handle = handle
        
        #Tytuł pola tekstowego
        self.add_widget(gtk.Label("Id testu: "))

        #Pole tekstowe
        self.test_entry = gtk.Entry()
        self.test_entry.set_size_request(200,25)
        self.test_entry.set_text('709rqd')
        self.add_widget(self.test_entry)

        #Separator
        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        separator.set_size_request(50,25)
        self.add_widget(separator)
        
        #Tytuł pola tekstowego
        self.add_widget(gtk.Label("Hasło: "))
        
        #Pole tekstowe
        self.pass_entry = gtk.Entry()
        self.pass_entry.set_size_request(300,25)
#        self.pass_entry.set_text('123123')
        self.add_widget(self.pass_entry)
        
        #Przycisk pobierania
        download_button = ToolButton("download")
        download_button.set_tooltip("Pobierz test")
        download_button.connect("clicked", handle.get_test_bt)
        self.add_widget(download_button)
        
    def add_widget(self, widget):
        tool_item = gtk.ToolItem()
        tool_item.add(widget)
        widget.show()
        self.insert(tool_item, -1)
        tool_item.show()

