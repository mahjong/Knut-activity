#encoding: utf-8

import gtk, pango

class TestsBrowser(gtk.VBox):
    def __init__(self, tests_list, handle):
        gtk.VBox.__init__(self)
        
        self.handle = handle
        self.tests_list = tests_list
        
        self.list_store = gtk.ListStore(str, str, str)
        self.tree_view = gtk.TreeView(self.list_store)
        self.tv_column1 = gtk.TreeViewColumn('tytuł')
        self.tv_column2 = gtk.TreeViewColumn('Instrukcje')
        self.tv_column3 = gtk.TreeViewColumn('Publiczny')
        for test in tests_list.test:
            self.list_store.append([test.title, test.instructions.text[:30], {'False': 'Tak', 'True': 'Nie'}[test.protected.__str__()] ])
        
        self.tree_view.append_column(self.tv_column1)
        self.tree_view.append_column(self.tv_column2)
        self.tree_view.append_column(self.tv_column3)
        
        self.cell1 = gtk.CellRendererText()
        self.cell2 = gtk.CellRendererText()
        self.cell3 = gtk.CellRendererText()
        
        self.tv_column1.pack_start(self.cell1, False)
        self.tv_column2.pack_start(self.cell2, False)
        self.tv_column3.pack_start(self.cell3, False)
        
        self.tv_column1.set_attributes(self.cell1, text=0)
        self.tv_column2.set_attributes(self.cell2, text=1)
        self.tv_column3.set_attributes(self.cell3, text=2)

        self.pack_start(self.tree_view, False, False, 30)
        
        self.download_btn = gtk.Button(" Pobierz test ")
        self.download_btn.connect("clicked", self.download_test)
    
        self.pack_start(self.download_btn, False, False, 30)
        
    def download_test(self, widget):
        iter = self.tree_view.get_selection().get_selected()[1]
        index = self.list_store.get_path(iter)[0]
        self.handle.chosen_test_id = self.tests_list.test[index].id_unq.text
        if self.tests_list.test[index].protected.text == 'false':
            self.handle.get_test_bt(check_pass=False)
        else: 
            self.handle.get_test_bt()
        
        