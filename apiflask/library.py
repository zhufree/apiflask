# -*- coding: utf-8 -*-

import urllib
import urllib2
import re

from bs4 import BeautifulSoup
import sys  
  
reload(sys)  
sys.setdefaultencoding('utf8')  
# successful condition
result = {"info": "", "status": True}
# wrong condition
error = {"reason": "", "status": False}



def bs(url, postdata=None):
    if postdata:
        return BeautifulSoup(urllib2.urlopen(
            urllib2.Request(url=url, data=postdata), timeout=5), 'lxml')
    else:
        return BeautifulSoup(urllib2.urlopen(
            urllib2.Request(url=url), timeout=5), 'lxml')

def handle_redirect_page(handle_url):
    redirectSoup = bs(handle_url)
    # to a redirect page
    # var url = 'http://metalib.lib.whu.edu.cn:80/
    # pds?func=sso&calling_system=aleph&pds_con_lng=CHI&url=http://opac.lib.whu.edu.cn:80/
    # F/.....-31913?func=bor-history-
    # loan&adm_library=WHU50&PDS_HANDLE=.....';
    rowurl = redirectSoup.find(text=re.compile(r"url\S"))
    # grab url from row url in this page
    pat = re.compile(r"url=(.*)\'")
    redirectUrl = re.search(pat, rowurl).group(1)
    # visit final page
    return redirectUrl


def getcookie(sid, pwd):  # 登录获得cookie字符串
    login_url = 'http://metalib.lib.whu.edu.cn/pds'  # 登录处理链接
    rowdata = {
        'func': 'login',
        'calling_system': 'mrbs',
        'bor_id': sid,
        'bor_verification': pwd,
        'institute': 'WHU',
        'url': 'http://metalib.lib.whu.edu.cn:80/pds?'
        } 
    postdata = urllib.urlencode(rowdata)  
    try:
        resultSoup = bs(login_url, postdata)  # 处理返回链接
        rawLink = resultSoup.find(
            "a", attrs={"href": re.compile("pds_handle")})  # 抓取含有pds_handle的链接
        pds_handle = re.search(r'pds_handle=\d+', rawLink["href"]).group().replace('pds_handle', 'PDS_HANDLE')
    except Exception, e:
        error["reason"] = e
        return error
    else:
        result['info'] = pds_handle  # 形成cookie字符串
        return result


# 查询历史借阅
def queryhistory(cookie):
    # 带cookie访问网址，转到登陆界面
    handle_url = 'http://opac.lib.whu.edu.cn:80/F/?func=bor-history-loan&adm_library=WHU50&{cookie}'.format(cookie=cookie)  # 历史借阅
    try:
        resultSoup = bs(handle_redirect_page(handle_url))
        tds = resultSoup.find_all('td', {'class': 'td1'})[1:]  # 抓取图书信息
        # print len(tds)
        # 10 td for info of one book
        all_books = []
        while len(tds)>=10:
            current_book_td = tds[0:10]
            current_book = {
                'BookNum': current_book_td[0].string,
                'BookAuthor': current_book_td[1].string,
                'BookName': current_book_td[2].string,
                'PublishYear': current_book_td[3].string,
                'ToDate': current_book_td[4].string,
                'ToTime': current_book_td[5].string,
                'FromDate': current_book_td[6].string,
                'FromTime': current_book_td[7].string,
                'Fines': current_book_td[8].string if current_book_td[8].string else str(0),
                'Location': current_book_td[9].string
            }
            print current_book
            all_books.append(current_book)# add current book into book list
            tds = tds[10:]# cut current book
    except Exception, e:
        error["reason"] = e
        return error
    else:
        result['info'] = all_books
        return result


# 查询当前借阅信息
def queryloan(cookie):
    # 带cookie访问网址，转到登陆界面
    # 历史借阅
    handle_url = 'http://opac.lib.whu.edu.cn:80/F/?func=bor-loan&adm_library=WHU50&{cookie}'.format(cookie=cookie)
    try:
        resultSoup = bs(handle_redirect_page(handle_url))
        tds = resultSoup.find_all(class_=re.compile("td1"))  # 抓取图书信息
        all_books = []  # 初始抓取的所有信息存在该列表
        book = {}  # 每本书以一个字典存储
        while len(tds)>=12:
            current_book_td = tds[0:12]
            current_book = {
                'BookNum': current_book_td[0].string.strip(),
                'BookAuthor': current_book_td[2].string,
                'BookName': current_book_td[3].string,
                'PublishYear': current_book_td[4].string,
                'ToDate': current_book_td[5].string,
                'ToTime': current_book_td[6].string,
                'Fines': current_book_td[7].string if current_book_td[7].string else str(0),
                'Location': current_book_td[8].string
            }
            all_books.append(current_book)# add current book into book list
            tds = tds[12:]# cut current book
    except Exception, e:
        error["reason"] = e
        return error
    else:
        result['info'] = all_books
        return result


# 全部续借
def renewall(cookie):
    # 带cookie访问网址，转到登陆界面
    # 历史借阅
    handle_url = 'http://opac.lib.whu.edu.cn:80/F/?func=bor-loan&adm_library=WHU50&%s&afedog-flow-item=A8EA28FAD1EB4BECBD4E42B29AF605ED' % cookie
    try:
        linkSoup = bs(handle_redirect_page(handle_url))
        row_link = linkSoup.find(
            "a", attrs={"href": re.compile("javascript:replacePage")})  # 抓取全部续借的链接
        # print row_link
        pat = re.compile(r"http://opac\S+\'")
        rn_link = pat.findall(row_link["href"])[0]
        resultSoup = bs(rn_link)  # 访问链接抓取页面
        success_info = resultSoup.find("div", attrs={"class": "title"}).string.encode('utf-8')
        if "续借不成功" in success_info:
            tds = resultSoup.find_all(class_=re.compile("td1"))
            detail = ','.join([s.encode('utf-8') for s in tds[8].strings])
            error["reason"] = detail
            return error
        elif "续借的单册" in success_info:
            result['info'] = "renewall success"
            return result
        else:
            error["reason"] = "unknow error"
            return error
    except Exception, e:
        error["reason"] = e
        return error


def renew(cookie, number):
    # 需要续借的图书编号，在查询时有提供
    # 带cookie访问网址，转到登陆界面
    # 历史借阅
    handle_url = 'http://opac.lib.whu.edu.cn:80/F/?func=bor-loan&amp;adm_library=WHU50&%s&afedog-flow-item=A8EA28FAD1EB4BECBD4E42B29AF605ED' % cookie
    try:
        linkSoup = bs(handle_redirect_page(handle_url))
        pat = re.compile(r"http://opac\S+50")
        com_rn_link = pat.findall(linkSoup.find(text=re.compile(r"strData\S")))[0] # 抓取续借的链接
        # http://opac.lib.whu.edu.cn:80/F/
        # M8GNRUPQ5MXC4JMQQG5DR6JT8GGYY4QSJTKFX6RMG22MKQ4ICS-01830?func=bor-renew-all
        # &renew_selected=Y&adm_library=WHU50"; 
        books_to_renew = linkSoup.find_all("input", attrs={"type": "checkbox"})
        # [<input name="c001110582000040" type="checkbox"/>]
        bookid = books_to_renew[number-1]["name"]
        rn_link = com_rn_link + "&" + bookid + "=Y"
        # &c001110582000040=Y
        resultSoup = bs(rn_link)
        info = resultSoup.find("div", attrs={"class": "title"}).string.encode('utf-8')
        if "续借不成功" in info:
            tds = resultSoup.find_all(class_=re.compile("td1"))
            detail = ','.join([s.encode('utf-8') for s in tds[8].strings])
            error["reason"] = detail
            return error
        elif "续借的单册" in info:
            result['info'] = "renew success"
            return result
        else:
            error["reason"] = "unknow error"
            return error
    except Exception, e:
        error["reason"] = e
        return error


# 按关键词检索图书
def searchbook(cookie, searchword):
    handle_url = 'http://opac.lib.whu.edu.cn:80/F/?func=find-b&%s&request=%s' % (cookie, searchword)
    try:
        do_search_url = handle_redirect_page(handle_url)
        resultSoup = bs(do_search_url)  # 抓取信息界面
        divs_1 = resultSoup.find_all('div', {'class': 'itemtitle'})
        # print divs_1
        '''eg.
        <div class="itemtitle">
            <a href="http://opac.lib.whu.edu.cn:80/F/ESLXECVFK9QP5JA3Q2VPXN6PFBDM4N9MMF33JSSV3GECPC8M7L-11824?func=full-set-set&amp;set_number=000130&amp;set_entry=000001&amp;format=999">\u7f16\u7a0b\u73e0\u7391\xa0:\xa0\u7eed</a> 
            <a href="javascript:open_window('http://opac.lib.whu.edu.cn:80/F/ESLXECVFK9QP5JA3Q2VPXN6PFBDM4N9MMF33JSSV3GECPC8M7L-11825?func=service-sfx&amp;doc_number=001083459&amp;line_number=0000&amp;service_type=RECORD');">
                <img alt="Use SFX services" border="0" src="http://opac.lib.whu.edu.cn:80/exlibris/aleph/u20_1/alephe/www_f_chi/icon/f-sfx.gif"/>
            </a>
            <script>fmt_issn("978-7-115-37372-4")</script>
        </div>
        '''
        conditions_1 = resultSoup.find_all('u')
        # print conditions_1
        '''eg.<u>馆藏复本:     3,已出借复本:     0</u>'''
        cover_all_1 = resultSoup.find_all(
            'td', {'class': 'cover'})  # 封面图片+二维码
        print cover_all_1
        '''
        <td class="cover" valign="top">
            <!--<a href=http://opac.lib.whu.edu.cn:80/F/HAL77AGTKRVJH82ICP5DGU85YJKT6XC2EE63LIXV3XNX7M8IL1-14105?func=full-set-set&set_number=000155&set_entry=000001&format=999 id="WHU01001083459">
                <script>doclist["WHU01001083459"]=1;</script>
                </a>-->
            <a href="http://opac.lib.whu.edu.cn:80/F/HAL77AGTKRVJH82ICP5DGU85YJKT6XC2EE63LIXV3XNX7M8IL1-14106?func=full-set-set&amp;set_number=000155&amp;set_entry=000001&amp;format=999" id="WHU01001083459">
                <img border="0" src="http://book.bookday.cn/book/cover?isbn=978-7-115-37372-4&amp;w=105&amp;h=105"/>
            </a>
        </td>
        '''
        cover_extra_1 = resultSoup.find_all(
            'td', {'class': 'cover', 'id': 'opac_qr'})  # 二维码
        covers_1 = [c for c in cover_all_1 if c not in cover_extra_1]  # 封面
        books_1 = [
            {
                'BookNum': str(i),
                'BookName': divs_1[i].next.string,
                'Condition': conditions_1[i].string,
                'Cond_link': conditions_1[i].parent['href'],
                'BookCover': covers_1[i].next.nextSibling.nextSibling.next['src']
            } for i in range(len(divs_1))]
        nextpageUrl = do_search_url+"func=short-jump&jump=11"
        nextpageRequest = urllib2.Request(nextpageUrl)  # 抓取头两页
        nextpageSoup = BeautifulSoup(
            urllib2.urlopen(nextpageRequest, timeout=10), 'lxml')
        divs_2 = nextpageSoup.find_all('div', {'class': 'itemtitle'})

        conditions_2 = resultSoup.find_all('u')
        cover_all_2 = resultSoup.find_all('td', {'class': 'cover'})
        cover_extra_2 = resultSoup.find_all(
            'td', {'class': 'cover', 'id': 'opac_qr'})
        covers_2 = [c for c in cover_all_2 if c not in cover_extra_2]
        books_2 = [
            {
                'BookNum': str(i),
                'BookName': divs_2[i].next.string.encode('utf-8'),
                'Condition': conditions_2[i].string,
                'Cond_link': conditions_2[i].parent['href'],
                'BookCover': covers_2[i].next.nextSibling.nextSibling.next['src']
            } for i in range(len(divs_2))]
        for book in books_2:
            if book not in books_1:
                books_1.append(book)
        if len(books_1) > 0:
            result['info'] = books_1
            return result
        else:
            result['info'] = "no result"
            return result
    except Exception, e:
        error["reason"] = e
        return error


# 按编号预约书籍
def orderbook(cookie, book_to_order):
    check_orderUrl = book_to_order['Cond_link']
    checkorderRequest = urllib2.Request(check_orderUrl + '&%s' % cookie)
    checkorderSoup = BeautifulSoup(
        urllib2.urlopen(checkorderRequest, timeout=10), 'lxml')
    order = checkorderSoup.find(
        'a', {'href': re.compile('func=item-hold-request')})
    if order:
        orderUrl = order['href']
        orderSoup = BeautifulSoup(
            urllib2.urlopen(urllib2.Request(orderUrl), timeout=10), 'lxml')
        orderForm = orderSoup.find('form')
        rootUrl_1 = orderForm['action']
        input_data_1 = orderSoup.find_all('input')
        orderData = {inp['name']: inp['value'] for inp in input_data_1[:-1]}
        orderData['PICKUP'] = orderSoup.find('option')['value']
        orderData = urllib.urlencode(orderData)
        orderRequest = urllib2.Request(
            rootUrl_1 + '&%s' % cookie, data=orderData)
        resultSoup = BeautifulSoup(urllib2.urlopen(orderRequest, timeout=10), 'lxml')
        if 'The following locations have been excluded from the Pickup Loaction list' in str(resultSoup):
            result['info'] = 'order succeed'
            return result
        else:
            error["reason"] = 'order failed'
            return error
    else:
        error["reason"] = "no aviliable order"
        return error


# 查询已预约书籍
def queryorder(cookie):
    orderPage = 'http://opac.lib.whu.edu.cn/F/?func=bor-hold&adm_library=WHU50&' \
                '%s&afedog-flow-item=A8EA28FAD1EB4BECBD4E42B29AF605ED' % cookie
    orders = []
    try:
        RedirectSoup = BeautifulSoup(
            urllib2.urlopen(urllib2.Request(orderPage)), 'lxml')
    except urllib2.URLError, e:
        error["reason"] = e
        return error
    else:
        js = RedirectSoup.find(text=re.compile(r"url\S"))
        p = re.compile(r"http://opac\S+\'")
        url_ = p.findall(js)[0]
        req2 = urllib2.Request(url=url_)  # 抓取登陆后要访问的网址
        try:
            querySoup = BeautifulSoup(
                urllib2.urlopen(req2, timeout=4), 'lxml')  # 抓取信息界面
        except urllib2.URLError, e:
            error["reason"] = e
            return error
        else:
            rawInfo = querySoup.find_all('td', {'class': 'td1'})  # 抓取所有预约相关信息
            allorderInfo = rawInfo[1:]  # 去掉开头的无关信息
            while len(allorderInfo) >= 13:  # 每13条为一条预约信息
                singleOrderL = allorderInfo[:13]
                singleOrder = {
                    'BookNum': singleOrderL[0].next.string.rstrip(),
                    'cancel_link': singleOrderL[0].next['href'],
                    'BookName': singleOrderL[2].string,
                    'From': singleOrderL[3].string,
                    'To': singleOrderL[4].string,
                    'Location': singleOrderL[6].string,
                    'ReturnTime': singleOrderL[7].string}  # 列表中重要信息对应存储在字典中
                orders.append(singleOrder)  # 单个预约信息加入列表中
                allorderInfo = allorderInfo[13:]
            result['info'] = orders
            return result


# 删除预约请求
def deleteorder(cookie, order_to_delete):
    infoUrl = order_to_delete['cancel_link']
    try:
        infoSoup = BeautifulSoup(
            urllib2.urlopen(urllib2.Request(infoUrl), timeout=10), 'lxml')
    except urllib2.URLError, e:
        error["reason"] = e
        return error
    else:
        delete_link = infoSoup.find(
            'a', {'href': re.compile(r'DELETE')})['href']
        try:
            resultSoup = BeautifulSoup(
                urllib2.urlopen(urllib2.Request(delete_link), timeout=10), 'lxml')
        except urllib2.URLError, e:
            error["reason"] = e
            return error
        else:
            print resultSoup
            if u'管理库' in str(resultSoup):
                result['info'] = 'cancel succeed'
                return result
            else:
                error['reason'] = 'cancel failed'
                return error

if __name__ == '__main__':

    cookie = getcookie('2013302480033','114028')['info']
    print cookie
    # print queryloan(cookie)
    # print renewall(cookie)
    # print renew(cookie, 1)
    booksinfo= searchbook(cookie,'编程珠玑')
    print booksinfo

    # print booksinfo[0]['condition']+booksinfo[0]['cond_link']
    # book_to_order=None
    # for book in booksinfo:
    #     if book['Num']=='2':
    #         book_to_order=book
    #     else:
    #         pass
    # #print book_to_order
    # if book_to_order:
    #     print orderbook(cookie,book_to_order)
    # print  queryorder(cookie)
    # orders=queryorder(cookie)
    # order_to_delete=None
    # for order in orders:
    #     if order['Num']=='1':
    #         order_to_delete=order

    # if order_to_delete:
    #     print deleteorder(cookie,order_to_delete)