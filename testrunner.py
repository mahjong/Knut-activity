#encoding: utf-8

from lxml import etree, objectify
from sugar.graphics.alert import NotifyAlert, Alert
from sugar import profile
import os
import gtk
import logging
import coverpanel, itempanel
import mimetools
import httplib
import urllib, urllib2

class RunTest():
    def __init__(self, handle):
        self.handle = handle
        
        self._logger = logging.getLogger('activity-knut')
        self._logger.setLevel(logging.DEBUG)
        #First log handler: outputs to a file  
        file_handler = logging.FileHandler('/home/wiktor/code/knut.log')
        file_formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)
        
        self.answers_dict = {}
        self.question_type = {}
        test_file = file(self.handle.test_path)
        self.test = objectify.parse(test_file).getroot()
        self.cover = coverpanel.CoverPanel(self, title=self.test.config.title.text, 
                                           duration=self.test.config.time.text,
                                           instructions=self.test.config.instructions.text,
                                           author=self.test.config.author.text)

        self.cover.start_button.connect("clicked", self._run_test)
        self.handle.set_canvas(self.cover)
        self.cover.show_all()
#        self._run_test()
    
    def _run_test(self, widget=None):
        self.cover.hide_all()
        self.total_items = len(self.test["item"])
        self.current_item = 0
        self.item_panel = itempanel.ItemPanel(self.test.item[self.current_item], self.current_item+1, self.total_items, handle=self)
#        self.item_panel = itempanel.ItemPanel(self.test.item[4], self.current_item+5, self.total_items, handle=self)
        self.item_panel.next_button.connect("clicked", self._next_item)
        self.handle.set_canvas(self.item_panel)
        self.item_panel.show_all()
        
    def _next_item(self, widget=None):
        item_id = self.item_panel.question_id
        answers = []
        if self.item_type in ('one', 'mul'):
            for index in xrange(len(self.correct_btn)):
                correct = self.correct_btn[index].get_active()
                answers.append(correct)
        elif self.item_type == 't/f':
            correct = self.t_correct_btn.get_active()
            answers.append(correct)
#            correct = self.f_correct_btn.get_active()
#            answers[1] = correct
        self.answers_dict[item_id] = answers 
        self.question_type[item_id] = self.item_type
        self.current_item += 1
        if self.current_item >= self.total_items:
            self._finish_test()
        else:
            self.item_panel = itempanel.ItemPanel(self.test.item[self.current_item], self.current_item+1, self.total_items, handle=self)
            self.item_panel.next_button.connect("clicked", self._next_item)
            self.handle.set_canvas(self.item_panel)
            self.item_panel.show_all()
            
    def _finish_test(self):      
        self.item_panel.hide_all()
        user_name = profile.get_nick_name()
        
        # downloading answers
        values = {'test-id': self.handle.test_id,
                'test-password': self.handle.test_pass,
                'user-name': user_name}
        data = urllib.urlencode(values)
        url = self.handle.server + '/answers_download/'
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        
        answers_file = open(self.handle.answers_path, "w")
        answers_file.write(response.fp.read())
        answers_file.close()      
        
        answers_xml = objectify.parse(self.handle.answers_path).getroot()
#        print self.answers_dict
        emr = objectify.ElementMaker()
#        emr._nsmap = {None : "http://kolos.math.uni.lodz.pl/~idzik84/kvml_results"}
        results_xml = emr.results()
        points = 0.0
        points_max = len(self.answers_dict)
        for item in answers_xml.item:
            item_id = item.get('id')
            user_ans = self.answers_dict[item_id]
            options_num = len(item.option)
            cumul = 0.0
            results_item = emr.item()
            results_item.set('id', item_id)
            for index in xrange(options_num):
                results_option = emr.option({True: 'true', False: 'false'}[user_ans[index]])
                results_item.append(results_option)
                if item.option[index].get('correct') == 'true':
                    if user_ans[index]:
                        cumul += 1.0
                elif item.option[index].get('correct') == 'false':
                    if not user_ans[index]:
                        cumul += 1.0
            answer_correct = False
            item_type = self.question_type[item_id]
            if item_type in ('one', 't/f'):
                if options_num == cumul:
                    points += 1.0
                    answer_correct = True
#                print 'after one', points
            elif item_type == 'mul':
                points += (cumul/options_num)
                if cumul == options_num:
                    answer_correct = True
#                print 'after mul', points
            results_item.set('all_correct', {True: 'true', False: 'false'}[answer_correct])
            results_xml.append(results_item)
        points_percentage = (points/points_max*100)
        self.handle.show_alert(title="Wyniki testu", msg="Twój wyniki to %s punktów na %s możliwych. Wynik wyrażony w procentach %2.1f%%" % (points, points_max, points_percentage))
    
#        print(etree.tostring(results_xml, pretty_print=True))
#        results_path = os.path.join(self.handle.data_path, "results.xml")
#        f = open(results_path, 'w')
#        f.write(etree.tostring(results_xml, pretty_print=True))
#        f.close()
        boundary = mimetools.choose_boundary()
        body_list = []
        body_list = ["--%s--"%boundary, "Content-Disposition: form-data; name=results_xml; filename=results.xml", 
                      "Content-Type: application/xml", "", etree.tostring(results_xml, pretty_print=True), "--%s--"%boundary, 
                      'Content-Disposition: form-data; name="login"', "", user_name, "--%s--"%boundary, 
                      'Content-Disposition: form-data; name="test-id"', "", self.handle.test_id, "--%s--"%boundary, 
                      'Content-Disposition: form-data; name="points"', "", str(points), "--%s--"%boundary,
                      'Content-Disposition: form-data; name="points-percentage"', "", '%2.1f' % points_percentage, "--%s--"%boundary]
        body = "\r\n".join(body_list)
        headers = {"content-type":"multipart/form-data; boundary=%s"%boundary, "content-length":str(len(body))}
        connection = httplib.HTTPConnection(self.handle.server.replace('http://',''))
        self._logger.debug(self.handle.server)
        connection.request("POST","/results_upload/", body, headers)
        response = connection.getresponse()
        re = response.read()
        if re == "OK":
            text = " Test wysłany "
        else:
            file = open(self.handle.data_path + '/error.html', 'w')
            file.write(re)
            file.close()
            text = " Nie wysłano testu "
            
        #usuwanie pozostałych plików
        for root, dirs, files in os.walk(self.handle.data_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name) )
            for name in dirs:
                os.rmdir(os.path.join(root, name) )
        self._logger.debug('koniec')
        
    def _alert_cb(self, widget=None, data=None):
        self.handle.remove_alert(widget)
        
        