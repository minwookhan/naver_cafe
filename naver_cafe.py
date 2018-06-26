#-*- coding: utf-8 -*-
#-*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from page_objects import PageElement, PageObject
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from urllib.request import urlretrieve
from pandas import DataFrame, Series
from naver_log import configure_logger
import pandas as pd
import logging, re, json, sys, time, os




logging.getLogger("selenium").setLevel(logging.INFO)
#FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
#logging.basicConfig(format=FORMAT)
# logging.getSelf.Logger("naverDN_logger").setLevel(logging.DEBUG)
# self.logger = logging.getLogger('naverDN_logger')


class LoginPage(PageObject):
    username = PageElement(id_='id')
    password = PageElement(name='pw')
    login = PageElement(class_name='btn_global')


class naver_cafe(webdriver.Firefox, webdriver.Chrome, webdriver.Ie):
    def __init__(self, browser, _cafe_name ):
        '''
        browser: browser Name : ie, Firefox, chrome
        CNF_JSON_OBJ: site1['cafe_name']['menuID']['searchType']['searchKeyword']
        '''
        options = Options()
        options.set_headless()
        self.BROWSER = browser

        if browser.lower() == "ie":
            webdriver.Ie.__init__(self)
        elif browser.lower() == "chrome":
            webdriver.Chrome.__init__(self)
        elif browser.lower() == "phantomjs":
            webdriver.PhantomJS.__init__(self)
        else:
            #webdriver.Firefox.__init__(self, firefox_options=options)
            webdriver.Firefox.__init__(self)

        #self.implicitly_wait(5)  
        #        self.self.logger = logger.getLogger('Naver dn logger')
        #self.maximize_window() 
        self.CAFE_NAME = _cafe_name
        self.Dn = naver_dn()
        self.logger = configure_logger('cls_logger', 'logging_config.json') 


        self.log_in('minuxx','minuxher') 

        self.get('http://cafe.naver.com/'+ _cafe_name)
        self.lst_menu = self.get_cafe_menu()


    def __del__(self):
        logging.warning(" CLASS OJBECT KILLED")
        os.system('pkill -f %s'% self.BROWSER)


    def log_in(self, _id, _pwd):

        self.get('https://nid.naver.com/nidlogin.login')
        self.page = LoginPage(self)
        self.page.username = 'minuxx'
        self.page.password = 'minuxher'
        self.page.login.click()
        self.find_element_by_xpath("//form[@id='frmNIDLogin']/fieldset/span[1]/a").click()
        self.find_element_by_xpath("//div[@id='login_maintain']/span[1]/a").click()
        self.logger.info('로그인 성공')

    def get_cafe_menu(self):
        '''
        Get the name, address of MENU in cafe as DataFrame format 
        '''

        _t = self.find_elements_by_xpath("//div[@class='cafe-menu-tit']/p[@class='down-btn']")
        for i in _t:
            i.click()

        _b =self.find_elements_by_xpath("//div[@id='cafe-menu']/div[@class='box-g-m']/ul/li/a")
        _lst_menu = []
        for c, i in enumerate(_b):
                _href= i.get_attribute('href')
                _menuid = re.search('menuid=([0-9]*)', _href)
                if _menuid == None:
                        _menuid = None
                else:
                        _menuid = _menuid.group(1)
                _lst_menu.append((c, i.text, _href, _menuid))

        labels =['Num','name_menu','addr_menu','menu_id']
        _df = pd.DataFrame.from_records(_lst_menu, columns= labels)
        
        return _df 

    def goto_cf_menu(self,_kw):
        self.switch_to_default_content()
        _df = self.get_cafe_menu()
        _name = _df[_df['name_menu'].str.contains(_kw)]['name_menu'].tolist()[0]
        _addr = _df[_df['name_menu'].str.contains(_kw)]['addr_menu']
        _menuid = _df[_df['name_menu'].str.contains(_kw)]['menu_id'].tolist()[0]

        self.switch_to_default_content() 

        if len(_addr) >1:
            print("Duplicated Menu Name, Give me longer name")
            sys.exit()
        else:
            self.get(_addr.tolist()[0])
            self.logger.debug("Moved to "+ self.where_ami('menu_name'))
            return {'cf_name': _name, 'menu_id': _menuid}


    def get_cafe_info(self):
        '''
            _id : cafe 번호
            _name: cafe 이름
            _addr: cafe base 주소
        '''
        self.switch_to.default_content()
        _id = self.find_element_by_xpath("//div[@id='front-cafe']/a").get_attribute('href')
        _id = re.search('clubid=([0-9]*)', _id).group(1)
        _name = self.find_element_by_xpath("//head/title").text
        _addr = re.search("http://cafe.naver.com/([\w]*)", self.current_url).group(0)
        return {'cf_name': _name, 'cf_id': _id, 'cf_addr': _addr}



    def get_lstArticles_currnet_page(self):
        todate= lambda x: time.strftime("%y.%m.%d") if bool(re.search("[/d]*:", x)) else x
        _lst=[]
        self.switch_to.default_content()
        _addr = self.get_cafe_info()['cf_addr']

        self.switch_to.frame('cafe_main')
        _f_chk_exist = lambda x : True  if len(x)!=0 else False
        articles=self.find_elements_by_xpath("//form[@name='ArticleList']/table[@class='board-box']/tbody/tr[@align='center']")

        for i in articles:
#                self.switch_to.frame('cafe_main')
                _t_addr=''
                _num = i.find_element_by_xpath(".//td/span[@class='m-tcol-c list-count']").text
                _title = i.find_element_by_xpath(".//td[@align='left']/span/span[@class='aaa']/a").text.strip()
                _id = i.find_element_by_xpath(".//td[@class='p-nick']/a/span[@class='wordbreak']").text
                _date = todate(i.find_elements_by_xpath(".//td[@class='view-count m-tcol-c']")[0].text)
                _atch_file = _f_chk_exist(i.find_elements_by_xpath(".//input[@class='list-i-upload']") )
                _t_addr = _addr+"/"+ _num 
                _lst.append((_num, _title, _id, _date, _atch_file, _t_addr))

        return _lst

    def search_q(self,searchBy='3', keyword="", date="all"):
            '''date: all, 1d, 1w, 1m, 6m, 1y, 2017-09-012017-12-10 searchBy = 1(전체), 3(작성자), 4(댓글내용), 5(댓글작성자) 
            '''
            _base_url = 'http://cafe.naver.com/ArticleSearchList.nhn?'
            _clubID = self.where_ami('cafe_id')
            _date = date
            _searchBy = searchBy
            _query= keyword
            _defaultValue = '1'
            _menuid= self.where_ami('menu_id')
            _search_url = _base_url+'search.clubid='+_clubID+'&'\
                                            +'search.searchdate='+ date+ '&'\
                                            +'search.searchBy='+ searchBy +'&'\
                                            +'search.query='+_query+'&'\
                                            +'search.defaultValue='+_defaultValue+'&'\
                                            +'search.menuid='+_menuid+'#'
            self.logger.debug(_search_url)
            self.get(_search_url) 

    def where_ami(self,_type=''):
        '''
        _type = cafe_name, menu_name, cafe_id, menu_id
           게시판의 즐겨찾기에서 1차로 정보를 빼온다.
           즐겨찾기가 없으면 여기저기서 줏어서 어째든 현재 열려진 페이지 정보를 알려준다
        '''
        if _type =="":
                print('알고싶은 정보를 Argument 로 입력하세요')
                print(' _type = cafe_name, menu_name, cafe_id, menu_id')
                sys.exit()

        self.switch_to_default_content()

        self.switch_to_frame('cafe_main')

        _t1 = self.find_elements_by_xpath("//div[@id='sub-tit']/h3/a[@id='favorite']")

        if len(_t1) == 1:

                _t1 = _t1[0]
                _t1 = _t1.get_attribute('onclick')
                _t2 = re.search(", ([0-9]*), ([0-9]*)\)", _t1)
                _cafe_id = _t2.group(1)
                _menu_id = _t2.group(2)
                _menu_name = self.find_element_by_xpath("//div[@id='sub-tit']/h3").text
                self.logger.debug("즐겨찾기 있음")
           
        else: 
                # 검색결과 화면에서 다시 검색할 때 동작한다. 이 전에 검색했던 게시판에서 다시 검색
                self.logger.debug("---즐겨찾기 없음")
                self.switch_to_default_content()
                _cafe_id = self.find_element_by_xpath("//div[@id='front-cafe']/a").get_attribute('href')
                _cafe_id = re.search('clubid=([0-9]*)', _cafe_id).group(1)
                self.switch_to.frame('cafe_main')
                _menu_name = self.find_element_by_xpath("//div[@id='sub-tit']/h3").text
                _menu_id = re.search("menuid=([0-9]*)", self.current_url).group(1)

        self.switch_to_default_content()
        _cafe_name = self.title.replace(_menu_name, "")
        result = {'cafe_name':_cafe_name, 'cafe_id':_cafe_id,'menu_id':_menu_id, 'menu_name':_menu_name}

        return result[_type]

 

    def __isExist_Next_page__(self):
        '''
            move to Next page in iFrmae(id='cafe_main') if next page is available
        '''
        self.switch_to.default_content()
        self.switch_to.frame('cafe_main')
        _t =  self.find_elements_by_xpath("//table[@class='Nnavi']/tbody/tr/td[@class='on']/following-sibling::td/a")
        if len(_t):

                self.logger.debug('Next Page Exist')

                return True

        else:
                self.logger.debug('Next Page dose not Exist')
                return False

    def __goTo_nextPage__(self):
        try:
            self.switch_to.default_content()
            self.switch_to.frame('cafe_main')
            _t = self.find_element_by_xpath("//div[@class='prev-next']/table[@class='Nnavi']/tbody/tr/td[@class='on']/following-sibling::td/a")
            self.logger.info(_t.text)
            _t.click()
        except:
            self.get(self.current_url)
            self.find_element_by_xpath("//div[@class='prev-next']/table[@class='Nnavi']/tbody/tr/td[@class='on']/following-sibling::td/a").click()


    def get_lst_whole_bulletin(self):
        ''''
        retrun Whole bulletin information
        '''
        labels =['Num','Title','Writer','Date','Atch_file','Addr']

        _lst=[]
        _lst = self.get_lstArticles_currnet_page()

        #self.logger.debug(_lst)
        while(self.__isExist_Next_page__()):
                self.__goTo_nextPage__()
                time.sleep(1) # 1초안주면 세션에러난다
                _t = self.get_lstArticles_currnet_page()
                _lst.extend(_t)
        #        self.self.logger.debug(_lst)
        _df = pd.DataFrame.from_records(_lst, columns= labels)
        _df = _df.drop_duplicates()
        print('{} scores are grabbed !'.format(len(_df)))
        return _df 


    def __get_download_file_nameNlinks__(self):
        

        '''
        RETURN a list : [(file1, link1),(file2, link2), (file3,link3)...]
        '''
        _txt_dn_arrow = "//div[@class='atch_file_area']/a[@class='atch_view m-tcol-c']"
        _txt_dn_box = "//div[@class='atch_file_area']/div[@id='attachLayer']"
        _txt_cafe_main = "//div[@class='cafe_main']"
        _txt_files = "//div[@id='attachLayer']/ul/li/span[@class='file_name']"
        _txt_dn_links = "//div[@id='attachLayer']/ul/li/div[@id='attahc']/a[1]"
        _txt_dn_close = "//div[@class='ly_atch_file']/a[@class='clse']"
        self.switch_to.default_content()
        self.switch_to.frame('cafe_main')

        self.logger.debug("getting nameNlinks")

        time.sleep(1)
        # try:

        #     dn_box = self.find_element_by_xpath(_txt_dn_box)
        # except NoSuchElementException  :
        #    logging.error(str(self.__get_title__())+' :Download 게시물이 아닙니다.')

        if not self.__check_exists_by_xpath__(_txt_dn_box):
            raise NoSuchElementException("this hasn't DOWNLOAD FILED") 

        self.find_element_by_xpath(_txt_dn_arrow).click()
        time.sleep(1) 
        _links_ = self.find_elements_by_xpath(_txt_dn_links)
        _files_ = self.find_elements_by_xpath(_txt_files)
        time.sleep(1)

        _dn_links = [i.get_attribute('href') for i in _links_]
        _dn_files = [i.text for i in _files_]

        # Close download file box
        self.find_element_by_xpath(_txt_dn_close).click()
        time.sleep(1) 
        return list(zip(_dn_links, _dn_files))


    def __insert_youtube_linksFile__(self, _fname):
        '''
        _fname: file_path and name
        create youtube html file if exist or
        do nothing
        '''
        self.switch_to.default_content()
        self.switch_to.frame('cafe_main')
        _path = "//iframe[contains(@src, 'youtube.com')]"
        _header = "<html><body>"
        _footer = "</body></html>"
#        import ipdb; ipdb.set_trace()

        self.logger.debug("*** Youtube Linke called *****")
        self.switch_to.default_content()
        self.switch_to.frame('cafe_main')

        if self.__check_exists_by_xpath__(_path):
            self.logger.debug('Youtube links found')
            _youtube_links = self.find_elements_by_xpath(_path)
            _youtube_src = "<p>".join([x.get_attribute('outerHTML') for x in _youtube_links])
            _youtube_src = _header + _youtube_src + _footer

            with open(_fname, 'w') as f:
                f.write(_youtube_src)
                f.close()
                
            return True
    
        else :
            return False


    def __get_title__(self):
        
        '''게시물을 읽기 상태에서만 동작'''
        self.switch_to.default_content()
        self.switch_to.frame('cafe_main')
        try:
            _t = self.find_element_by_xpath("//span[@class='b m-tcol-c']").text.strip()

        except NoSuchElementException :
            print("게시물안이 아닙니다")
        else:
            return _t

    

    def download_in_page(self, _folder ='./'):
        '''
        Download all files in open page
        and return the list of FILES and TITLE
        '''
        try: 
            _lst_files = self.__get_download_file_nameNlinks__()
        except Exception as E:
            self.logger.error(E)

        else:

            _title_  = self.__get_title__()
            self.switch_to_default_content()
            self.switch_to.frame('cafe_main')
            _date_ = self.find_element_by_xpath("//td[@class='m-tcol-c date']").text
            _date_ = re.sub("\.", "-", re.search("[\d]{4}.[\d]{2}.[\d]{2}", _date_).group(0))


            if _folder =='./':
                _folder = './'+ _date_ + '  '+ _title_
            else:
                if not(_folder.endswith('/')):

                    _folder = _folder+ '/' + _date_ + " " + _title_

            if os.path.exists(_folder):
                pass
            else:
                os.makedirs(_folder)

            lst_down_success =[]
            lst_down_fail = []
            for i in _lst_files:
                try:
                    #i[0] : addr of file, i[1] : filename
                    self.logger.info(i[1])
                    self.Dn.save(i[0], _folder+'/'+ i[1])
                    self.__insert_youtube_linksFile__(_folder+'/'+  _title_+'.html')
                    lst_down_success.append(i[1])  #

                except :
                    lst_down_fail.append(i[1])
                    logging.error('\nDownloading error')
                    return lst_down_fail

            lst_down_success.append(_title_)
            return lst_down_success


    def __check_exists_by_xpath__(self, xpath):
        try:
            self.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True


class naver_dn:
    def __init__(self):
        pass
    def _reporthook_(self, count, block_size, total_size):

        global start_time
        if count == 0:
            start_time = time.time()
            return
        duration = time.time() - start_time
        progress_size = int(count * block_size)
        speed = int(progress_size / (1024 * duration))
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write("\r...%d%%, %.2f MB, %d KB/s, %d seconds passed" %
                        (percent, progress_size / (1024 * 1024), speed, duration))
        sys.stdout.flush()


    def save(self, url, path_filename):
        print('{} is downloading '.format(path_filename))
        try:
            urlretrieve(url, path_filename, self._reporthook_)
        except Exception:
            self.logger.Error('urlretrieve Error')
            raise Exception("urlretrieve Error")



