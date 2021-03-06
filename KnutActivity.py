#encoding: utf-8

from sugar.activity import activity
from sugar import logger

import testtoolbar, itempanel, testrunner
from testrunner import RunTest
from testtoolbar import TestToolbar
from browsetoolbar import BrowseToolbar
import gtk, os
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.alert import Alert, NotifyAlert, Icon
import time
import mimetools
import tarfile
import httplib
from sugar import profile
import logging
import urllib, urllib2


class KnutActivity(activity.Activity):	

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self.test_cover = False
        self.chosen_test_id = None
        
        self.data_path = os.path.join(self.get_activity_root(), "data")
        self.instance_path = os.path.join(self.get_activity_root(), "instance")
        self.test_path = os.path.join(self.data_path, "test.xml")
        self.questions_path = os.path.join(self.data_path, "questions.tar.bz2")
        self.answers_path = os.path.join(self.data_path, "answers.xml")
        self.server_settings_path = os.path.join(self.instance_path, "settings.txt")
        try:
            fin = open(self.server_settings_path, 'rw')
            self.server = fin.read()
            fin.close()
        except:
            self.server = 'localhost:8000'
        
        self.set_title("Test client")
        self.alerts_list = []

        # pasek narzędziowy
        toolbox = activity.ActivityToolbox(self)
        activity_toolbar = toolbox.get_activity_toolbar()

        # usuniecie niepotrzebnych przycisków
        activity_toolbar.share.props.visible = False
        activity_toolbar.keep.props.visible = False
        #activity_toolbar.stop.props.visible = False
        tool_item = gtk.ToolItem()
        lab_settings = gtk.Label('Adres Serwera: ')
        tool_item.add(lab_settings)
        lab_settings.show()
        activity_toolbar.insert(tool_item, 4)
        tool_item.show()
        
        tool_item = gtk.ToolItem()
        self.server_entry = gtk.Entry()
        self.server_entry.set_size_request(200,25)
        self.server_entry.set_text(self.server)
        tool_item.add(self.server_entry)
        self.server_entry.show()
        activity_toolbar.insert(tool_item, 5)
        tool_item.show()
        
        save_button = ToolButton("dialog_ok")
        save_button.set_tooltip("Zapisz")
        save_button.connect("clicked", self.save_server)
        tool_item = gtk.ToolItem()
        tool_item.add(save_button)
        save_button.show()
        activity_toolbar.insert(tool_item, 6)
        tool_item.show()
        

        # dodanie paska dla testów
        self.test_toolbar = TestToolbar(self)
        toolbox.add_toolbar("Test", self.test_toolbar)
        self.test_toolbar.show()
        
        # dodanie paska do przeglądania testów na serwerze
        self.browse_toolbar = BrowseToolbar(self)
        toolbox.add_toolbar("Przeglądaj testy", self.browse_toolbar)
        self.browse_toolbar.show()
        
#        self.settings_toolbar = SettingsToolbar(self)
#        toolbox.add_toolbar("Ustawienia", self.test_toolbar)
#        self.settings_toolbar.show()
        self.set_toolbox(toolbox)
        
        toolbox.show()
        
    def save_server(self, widget=None, data=None):
        """
        Zapisuje ustawienia serwera
        """
        server = self.server_entry.get_text()
        if server:
            if server.find('http://') == -1:
                server = 'http://' + server
            fout = open(self.server_settings_path, 'w')
            self.server = server
            fout.write(server)
            fout.close()
            self.show_alert(title="Edycja ustawień testu %s" % self.test_id, msg="Zapisano adres serwera")            
        
    def get_test_bt(self, widget=None, data=None, check_pass=True):
        self.clear_alerts()
        try:
            if self.chosen_test_id:
                self.test_id = self.chosen_test_id
                self.chosen_test_id = None
                self.test_pass = self.browse_toolbar.pass_entry.get_text()
            else:
                self.test_pass = self.test_toolbar.pass_entry.get_text()
                self.test_id = self.test_toolbar.test_entry.get_text()
            #sprawdzenie czy istnieje
            if check_pass and not self.test_pass:
                self.show_alert(title="Pobieranie testu %s" % self.test_id, msg="Hasło jest wymagane")
            elif not self.test_id:
                self.show_alert(title="Pobieranie testu %s" % self.test_id, msg="Pole z Id testu jest wymagane")
            else:
                self.user_name = profile.get_nick_name()
                self.test_pass = self.test_pass
                values = {'test-id': self.test_id,
                        'test-password': self.test_pass,
                        'user-name': self.user_name}
                data = urllib.urlencode(values)
                url = self.server + '/questions_download/'
                req = urllib2.Request(url, data)
                response = urllib2.urlopen(req)
                
                questions_file = open(self.questions_path, "w")
                questions_file.write(response.fp.read())
                questions_file.close()
                
                questions_file = tarfile.open(self.questions_path,"r")
                questions_file.extractall(path=self.data_path)
                os.remove(self.questions_path)
                
                
                
#                user_name = profile.get_nick_name()
#                test_pass = self.test_toolbar.pass_entry.get_text()
#                body_list = ["--%s--"%boundary,"Content-Disposition: form-data; name=test-id", "", self.test_id, "--%s--"%boundary,
#                             "Content-Disposition: form-data; name=test-password", "", test_pass, "--%s--"%boundary,
#                             "Content-Disposition: form-data; name=user_name", "", user_name, "--%s--"%boundary]
#                body = "\r\n".join(body_list)
#                headers = {"Content-Type": "multipart/form-data; boundary=%s"%boundary, "Content-Length": str(len(body))}
#                connection = httplib.HTTPConnection(self.server)
#                connection.request("POST","/questions_download/", body, headers)
#                response = connection.getresponse()
#                if response.reason != "OK":
#                    print response.reason
#                    print response.read()
#                
#                questions_file = open(self.questions_path, "w")
#                questions_file.write(response.fp.read())
#                questions_file.close()
#                
#                connection = httplib.HTTPConnection(self.server)
#                connection.request("POST","/answers_download/", body, headers)
#                response = connection.getresponse()
#                if response.reason != "OK":
#                    print response.reason
#                    print response.read()
#                
#                answers_response = response.fp.read()
#                answers_file = open(self.answers_path, "w")
#                answers_file.write(answers_response)
#                answers_file.close()
#                
#                #wypakowanie testu
#                questions_file = tarfile.open(self.questions_path,"r")
#                questions_file.extractall(path=self.data_path)
#                os.remove(self.questions_path)
                
                self.show_alert(title="Pobieranie testu %s" % self.test_id, msg="Pobieranie testu zakończone sukcesem, kliknij ok aby kontynuować", start_test=True)
                #urlretrieve(url+"test.zip", zip_path)
                #xmlschema_doc = etree.parse("kvml.xsd")
                #
                ##os.chdir(self.handle.instance_path)
                ##os.popen("unzip -o test.zip", "r")
                #
                #f_test = file(self.handle.test_path)
                #if (f_test.readline() == "Nie odnaleziono pliku"):
                #    msg = "Nie udało się pobrać testu"
                #    f_test.close()
                #else:
                #    f_test.close()
                    
                    ##walidacja przy użyciu XMLSchema
                    #xmlschema = etree.XMLSchema(xmlschema_doc)
                    #test_doc = etree.parse(file(self.handle.test_path))
                    #if xmlschema.validate(test_doc):
                    #    msg = "Test pobrany poprawnie"
                    #    self.handle.test_cover = True
                    #else:
                    #    msg = "Pobrany test nie jest zgodny ze standardem"
        except:
            self._logger = logging.getLogger('activity-knut')
            self._logger.setLevel(logging.DEBUG)
            #First log handler: outputs to a file  
            file_handler = logging.FileHandler('/home/wiktor/code/knut.log')
            file_formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(file_formatter)
            self._logger.addHandler(file_handler)
            self._logger.exception('Pobieranie testu')
            self.show_alert(title="Pobieranie testu %s" % self.test_id, msg="Nie udało się pobrać testu, skontaktuj się z nauczycielem")
                   
    def show_alert(self, title='', msg='', start_test = False):
        alert = Alert()
        alert.props.title = title
        alert.props.msg = msg
        alert.add_button(gtk.RESPONSE_OK, '  OK  ')
        alert.connect('response', self.alert_response_cb, start_test)
        self.add_alert(alert)
        self.alerts_list.append(alert)
        alert.show()
        
    def clear_alerts(self):
        for alert in self.alerts_list:
            self.remove_alert(alert)

    def alert_response_cb(self, alert, response_id, start_test=''):
        self.remove_alert(alert)
        if start_test:
            self.test=testrunner.RunTest(self)
          
    def alert_get_test_response(self, widget=None, data=None):
        self.remove_alert(widget)
        self.read_test()
            
            