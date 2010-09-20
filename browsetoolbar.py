#encoding: utf-8
import gtk
import logging
import urllib2
import urllib

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.combobox import ComboBox

from testsbrowser import TestsBrowser

from lxml import objectify

class BrowseToolbar(gtk.Toolbar):
    
    TEST_CATEGORIES = {0: 'Różności',
                       1: 'Matematyka',
                       2: 'Informatyka',
                       3: 'Geografia',
                       4: 'Historia'}
    
    def __init__(self, handle):
        gtk.Toolbar.__init__(self)
        
        self.handle = handle
        self._logger = logging.getLogger('activity-knut')
        self._logger.setLevel(logging.DEBUG)
        #First log handler: outputs to a file  
        file_handler = logging.FileHandler('/home/wiktor/code/knut.log')
        file_formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)
        
        #Tytuł pola tekstowego
        self.add_widget(gtk.Label("Kategoria: "))

        #Pole tekstowe
        self.test_type = ComboBox()
        for id, name in BrowseToolbar.TEST_CATEGORIES.items():
            self.test_type.append_item(id, name)
        self.test_type.set_active(0)
        self.add_widget(self.test_type)

        #Separator
#        separator = gtk.SeparatorToolItem()
#        separator.set_draw(True)
#        separator.set_size_request(50,25)
#        self.add_widget(separator)
        
        #Tytuł pola tekstowego
        self.add_widget(gtk.Label(" Szukaj w tytule: "))
        
        #Pole tekstowe
        self.search_entry = gtk.Entry()
        self.search_entry.set_size_request(100,25)
#        self.pass_entry.set_text('123123')
        self.add_widget(self.search_entry)
        
        #Przycisk pobierania
        download_button = ToolButton("download")
        download_button.set_tooltip("Przeglądaj testy")
        download_button.connect("clicked", self.list_download)
        self.add_widget(download_button)
        
        separator2 = gtk.SeparatorToolItem()
        separator2.set_draw(True)
        separator2.set_size_request(50,25)
        self.add_widget(separator2)
        
        self.add_widget(gtk.Label("Hasło: "))
        self.pass_entry = gtk.Entry()
        self.pass_entry.set_size_request(100,25)
#        self.pass_entry.set_text('123123')
        self.add_widget(self.pass_entry)
        
    def add_widget(self, widget):
        tool_item = gtk.ToolItem()
        tool_item.add(widget)
        widget.show()
        self.insert(tool_item, -1)
        tool_item.show()

    def list_download(self, widget):
        self._logger.debug('list_download')
        category_id = self.test_type.value
        category = BrowseToolbar.TEST_CATEGORIES[category_id]
        self._logger.debug('%s'% (category))
        search = self.search_entry.get_text()
        self._logger.debug(search)
        data = {'cat': category,
                'search': search}
        url_values = urllib.urlencode(data)
        url = self.handle.server + '/test_list_all/?' + url_values
        self._logger.debug(url)
        response = urllib2.urlopen(url)
        tests_xml = response.read()
        self.tests_list = objectify.fromstring(tests_xml)
        self._logger.debug('xml:%s' % tests_xml)
        self._logger.debug('objectified:%s' % self.tests_list.countchildren())
        if self.tests_list.countchildren() > 0:
            tests_browser = TestsBrowser(self.tests_list, self.handle)
            self.handle.set_canvas(tests_browser)
            tests_browser.show_all()
        else:
            self.handle.set_canvas(gtk.Label())
            self.handle.show_alert(title="Pobieranie listy testów", msg="Na serwerze nie testów z wybranej kategorii, spróbuj inną")
