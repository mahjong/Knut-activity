#encoding: utf-8

import gtk, pango
from lxml import objectify, etree
import os

class ItemPanel(gtk.VBox):
    def __init__(self, test_item, current_item, total_items, handle):
        gtk.VBox.__init__(self)
        
        data_path = os.path.join(handle.handle.get_activity_root(), "data")
        self.question_id = test_item.get("id")
        
        title_label = gtk.Label("Pytanie %s/%s"%(current_item,total_items))
        title_label.modify_font(pango.FontDescription("serif bold italic 30"))
        eb = gtk.EventBox()
        eb.set_size_request(0,100)
        eb.add(title_label)
        eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("blue"))
        self.pack_start(eb, False, False, 0)  
        question_vbox = gtk.VBox()
        question = gtk.Label(test_item.question.text)
        question.set_line_wrap(True)
        question.modify_font(pango.FontDescription("serif bold  24"))
        question.set_justify(gtk.JUSTIFY_CENTER)
        question.set_size_request(1000,100)
        question_vbox.pack_start(question, False, False)
        img = test_item.question.get('img')
        if img:
            img_filename = os.path.join(data_path, str(current_item), img)
            q_pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(img_filename, 200, 100)
            q_image = gtk.image_new_from_pixbuf(q_pixbuf)
            question_vbox.pack_start(q_image, False, False , 5)
        
        self.pack_start(question_vbox, False, False, 0)

        item_type = test_item.get('type')
        handle.item_type = item_type
        index = 0
        if item_type in ('one', 'mul'):
            labels = {}
            text_view_hbox = {}
            self.correct_btn = {}
            option_vbox = {}
            table = gtk.Table(2,2,False)
            table.set_row_spacings(10)
            table.set_col_spacings(10)
            for option in test_item.option:
                if option.text:
                    labels[index] = gtk.Label(option.text)
                else:
                    labels[index] = gtk.Label()
                labels[index].set_line_wrap(True)
                if item_type == 'one':
                    if index == 0:
                        self.correct_btn[0] = gtk.RadioButton()
                    else:
                        self.correct_btn[index] = gtk.RadioButton(self.correct_btn[0])
                elif item_type == 'mul':
                    self.correct_btn[index] = gtk.CheckButton()
                text_view_hbox[index] = gtk.HBox(False, 0)
                text_view_hbox[index].pack_start(labels[index], False, False, 100)


                img = option.get('img')
                if img:
                    img_filename = os.path.join(data_path, str(current_item), img)
                    op_pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(img_filename, 200, 100)
                    op_image = gtk.image_new_from_pixbuf(op_pixbuf)
                    text_view_hbox[index].pack_start(op_image, False, False , 5)
                text_view_hbox[index].pack_start(self.correct_btn[index], False, False, 0)
                option_vbox[index] = gtk.VBox(False, 0)
                option_vbox[index].pack_start(text_view_hbox[index], False, False, 0)
                if index == 0:
                    table.attach(option_vbox[index], 0, 1, 0, 1)
                elif index == 1:
                    table.attach(option_vbox[index], 0, 1, 1, 2)
                elif index == 2:
                    table.attach(option_vbox[index], 1, 2, 0, 1)
                elif index == 3:
                    table.attach(option_vbox[index], 1, 2, 1, 2)
                index += 1
            self.pack_start(table, False, False, 10)
            handle.correct_btn = self.correct_btn

        elif item_type == 't/f':
            t_label = gtk.Label(' Prawda ')
            f_label = gtk.Label(' Fałsz ')
            t_correct_btn = gtk.RadioButton()
            f_correct_btn = gtk.RadioButton(t_correct_btn)
            t_hbox = gtk.HBox(False, 0) 
            t_hbox.pack_start(t_label, False, False, 0)
            t_hbox.pack_start(t_correct_btn, False, False, 0)
            f_hbox = gtk.HBox(False, 0) 
            f_hbox.pack_start(f_label, False, False, 0)
            f_hbox.pack_start(f_correct_btn, False, False, 0)
            tf_hbox = gtk.HBox(False, 0)
            tf_hbox.pack_start(t_hbox, False, False, 300)
            tf_hbox.pack_start(f_hbox, False, False, 0)
            self.pack_start(tf_hbox, False, False, 0)
            handle.t_correct_btn = t_correct_btn
            handle.f_correct_btn = f_correct_btn

#        hbox = gtk.HBox()
#        answer = gtk.TextView()
#        self.text_buffer = answer.get_buffer()
#        answer.modify_font(pango.FontDescription("serif bold 16"))
#        answer.set_size_request(800,160)
#        answer.set_wrap_mode(gtk.WRAP_WORD)
#        answer.set_left_margin(20)
#        answer.set_right_margin(20)
#        hbox.pack_start(answer, True, False, 0)
        
#        self.pack_start(hbox, False, False, 0)
        self.next_button = gtk.Button(" Następne pytanie ")

        if self.next_button.get_use_stock():
            label = self.next_button.child.get_children()[1]
        elif isinstance(self.next_button.child, gtk.Label):
            label = self.next_button.child
        else:
            raise ValueError("button does not have a label")
        
        label.modify_font(pango.FontDescription("serif 16"))
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(self.next_button, True, False, 0) 
        self.pack_start(hbox, False, False, 100)
        