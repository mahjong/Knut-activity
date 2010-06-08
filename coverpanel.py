#encoding: utf-8

import gtk, pango

class CoverPanel(gtk.VBox):
    def __init__(self, handle, title, duration, instructions, author):
        gtk.VBox.__init__(self)
        
        title_label = gtk.Label(title)
        title_label.modify_font(pango.FontDescription("serif bold italic 30"))
        eb = gtk.EventBox()
        eb.set_size_request(0,100)
        eb.add(title_label)
        eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("blue"))
        self.pack_start(eb, False, False, 0)  
        
        duration_label = gtk.Label("Czas: %s minut"%duration)
        duration_label.modify_font(pango.FontDescription("serif bold  16"))
        duration_label.set_justify(gtk.JUSTIFY_CENTER)
        duration_label.set_size_request(0,100)
        self.pack_start(duration_label, False, False, 0)
        
        vbox = gtk.VBox()

        instructions_label1 = gtk.Label("Instrukcje:")
        instructions_label1.modify_font(pango.FontDescription("serif bold 20"))
        #instructions_label1.set_size_request(100,100)
        vbox.pack_start(instructions_label1, True, False, 0)
        
        instructions_label = gtk.Label(instructions)
        instructions_label.modify_font(pango.FontDescription("serif 16"))
        instructions_label.set_line_wrap(True)
        #instructions_label.set_size_request(1000,200)
        vbox.pack_start(instructions_label, True, False, 0)
        self.pack_start(vbox, False, False, 50)
        
        author_label = gtk.Label(author)
        author_label.modify_font(pango.FontDescription("serif 16"))
        author_label.set_line_wrap(True)
#        author_label.set_size_request(0,50)
        self.pack_start(author_label, False, False, 0)
        
        self.start_button = gtk.Button(" Rozpocznij Test ")

        if self.start_button.get_use_stock():
            label = self.start_button.child.get_children()[1]
        elif isinstance(self.start_button.child, gtk.Label):
            label = self.start_button.child
        else:
            raise ValueError("button does not have a label")
        
        label.modify_font(pango.FontDescription("serif 16"))
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(self.start_button, True, False, 0) 
        self.pack_start(hbox, False, False, 30)
        