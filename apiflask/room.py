#  -*-coding: utf-8-*-

import urllib
import urllib2
import xml.etree.ElementTree as ET
import re
import datetime
import sys

from bs4 import BeautifulSoup

from book import bs, getcookie

reload(sys)
sys.setdefaultencoding("utf-8")

now = datetime.datetime.now()

#  抓取空闲研修室的方法，输出格式见API文档

# successful condition
result = {"info": "", "status": True}
# wrong condition
error = {"reason": "", "status": False}


def get_room_info(region, year=now.year, month=now.year,day=now.day):
    # 获取空闲研修室信息，参数为年月日和学部（1是本部，2是医学部）
    check_base_url = 'http://reserv.lib.whu.edu.cn/day.php?year={year}&month={month}&day={day}'.format(
        year=year, month=month, day=day)
    room_dict = {}
    # 返回字典格式见文档
    # 返回四个时间段分别空闲的房间号, 按时间存储
    # 本部
    if region == '1':
        room_dict['B1.2'] = {'1': [], '2': [], '3': [], '4': []}   # area=6
        room_dict['B1.4'] = {'1': [], '2': [], '3': [], '4': []}   # area=8
        room_dict['B1.8-12'] = {'1': [], '2': [], '3': [], '4': []}   # area=8
        room_dict['B2.2'] = {'1': [], '2': [], '3': [], '4': []}   # area=9
        # 根据日期和area访问相应页面（6，8，9是本部的三个区域）
        area_6_soup = bs(check_base_url + '&area={area}'.format(area=6))
        area_8_soup = bs(check_base_url + '&area={area}'.format(area=8))
        area_9_soup = bs(check_base_url + '&area={area}'.format(area=9))
        empty_room_6 = area_6_soup.find_all('a', {'class': 'new_booking'})
        empty_room_8 = area_8_soup.find_all('a', {'class': 'new_booking'})
        empty_room_9 = area_9_soup.find_all('a', {'class': 'new_booking'})
        # print empty_room_6, empty_room_8, empty_room_9
        # 抓取可以预订的空闲研修室链接
        for i in empty_room_6:
            room = re.search(r"room=\d+", i['href']).group()
            hour = re.search(r"hour=\d+", i['href']).group()
            if hour == "hour=08":
                room_dict['B1.2']['1'].append(room[5:])
            elif hour == "hour=11":
                room_dict['B1.2']['2'].append(room[5:])
            elif hour == "hour=15":
                room_dict['B1.2']['3'].append(room[5:])
            elif hour == "hour=18":
                room_dict['B1.2']['4'].append(room[5:])
        # 判断空闲时间段，并加入该研修室列表中，下同
        for i in empty_room_8:
            room = re.search(r"room=\d+", i['href']).group()
            hour = re.search(r"hour=\d+", i['href']).group()
            if room == "room=105":
                if hour == "hour=08":
                    room_dict['B1.8-12']['1'].append(room[5:])
                elif hour == "hour=11":
                    room_dict['B1.8-12']['2'].append(room[5:])
                elif hour == "hour=15":
                    room_dict['B1.8-12']['3'].append(room[5:])
                elif hour == "hour=18":
                    room_dict['B1.8-12']['4'].append(room[5:])
            else:
                if hour == "hour=08":
                    room_dict['B1.4']['1'].append(room[5:])
                elif hour == "hour=11":
                    room_dict['B1.4']['2'].append(room[5:])
                elif hour == "hour=15":
                    room_dict['B1.4']['3'].append(room[5:])
                elif hour == "hour=18":
                    room_dict['B1.4']['4'].append(room[5:])
        for i in empty_room_9:
            room = re.search(r"room=\d+", i['href']).group()
            hour = re.search(r"hour=\d+", i['href']).group()
            if hour == "hour=08":
                room_dict['B2.2']['1'].append(room[5:])
            elif hour == "hour=11":
                room_dict['B2.2']['2'].append(room[5:])
            elif hour == "hour=15":
                room_dict['B2.2']['3'].append(room[5:])
            elif hour == "hour=18":
                room_dict['B2.2']['4'].append(room[5:])
        result['info'] = room_dict
        return result
    # 医学部
    elif region == '2':
        room_dict['Y1-2'] = {'1': [], '2': [], '3': [], '4': []}  # area=12
        room_dict['Y3-10'] = {'1': [], '2': [], '3': [], '4': []}  # area=14
        area_12_soup = bs(check_base_url + '&area={area}'.format(area=12))
        area_14_soup = bs(check_base_url + '&area={area}'.format(area=14))
        empty_room_12 = area_12_soup.find_all('a', {'class': 'new_booking'})
        empty_room_14 = area_14_soup.find_all('a', {'class': 'new_booking'})
        # print empty_room_12,empty_room_14
        for i in empty_room_12:
            room = re.search(r"room=\d+", i['href']).group()
            hour = re.search(r"hour=\d+", i['href']).group()
            print room, hour
            if hour == "hour=08":
                room_dict['Y1-2']['1'].append(room[5:])
            elif hour == "hour=11":
                room_dict['Y1-2']['2'].append(room[5:])
            elif hour == "hour=15":
                room_dict['Y1-2']['3'].append(room[5:])
            elif hour == "hour=18":
                room_dict['Y1-2']['4'].append(room[5:])
        for i in empty_room_14:
            room = re.search(r"room=\d+", i['href']).group()
            hour = re.search(r"hour=\d+", i['href']).group()
            print room, hour
            if hour == "hour=08":
                room_dict['Y3-10']['1'].append(room[5:])
            elif hour == "hour=11":
                room_dict['Y3-10']['2'].append(room[5:])
            elif hour == "hour=15":
                room_dict['Y3-10']['3'].append(room[5:])
            elif hour == "hour=18":
                room_dict['Y3-10']['4'].append(room[5:])
        result['info'] = room_dict
        return result
    elif region == '3':
        room_dict['G1-2'] = {'1': [], '2': [], '3': [], '4': []}  # area=12
        room_dict['G1-3'] = {'1': [], '2': [], '3': [], '4': []}  # area=12
        room_dict['G3-5'] = {'1': [], '2': [], '3': [], '4': []}  # area=12
        room_dict['G3-8'] = {'1': [], '2': [], '3': [], '4': []}  # area=12
        area_16_soup = bs(check_base_url + '&area={area}'.format(area=16))
        area_17_soup = bs(check_base_url + '&area={area}'.format(area=17))
        empty_room_16 = area_16_soup.find_all('a', {'class': 'new_booking'})
        empty_room_17 = area_17_soup.find_all('a', {'class': 'new_booking'})
        # print empty_room_12,empty_room_14
        for i in empty_room_16:
            room = re.search(r"room=\d+", i['href']).group()
            hour = re.search(r"hour=\d+", i['href']).group()
            if room == "room=107":
                if hour == "hour=08":
                    room_dict['G1-2']['1'].append(room[5:])
                elif hour == "hour=11":
                    room_dict['G1-2']['2'].append(room[5:])
                elif hour == "hour=15":
                    room_dict['G1-2']['3'].append(room[5:])
                elif hour == "hour=18":
                    room_dict['G1-2']['4'].append(room[5:])
            else:
                if hour == "hour=08":
                    room_dict['G1-3']['1'].append(room[5:])
                elif hour == "hour=11":
                    room_dict['G1-3']['2'].append(room[5:])
                elif hour == "hour=15":
                    room_dict['G1-3']['3'].append(room[5:])
                elif hour == "hour=18":
                    room_dict['G1-3']['4'].append(room[5:])
        for i in empty_room_17:
            room = re.search(r"room=\d+", i['href']).group()
            hour = re.search(r"hour=\d+", i['href']).group()
            if room == "room=112":
                if hour == "hour=08":
                    room_dict['G3-5']['1'].append(room[5:])
                elif hour == "hour=11":
                    room_dict['G3-5']['2'].append(room[5:])
                elif hour == "hour=15":
                    room_dict['G3-5']['3'].append(room[5:])
                elif hour == "hour=18":
                    room_dict['G3-5']['4'].append(room[5:])
            else:
                if hour == "hour=08":
                    room_dict['G3-8']['1'].append(room[5:])
                elif hour == "hour=11":
                    room_dict['G3-8']['2'].append(room[5:])
                elif hour == "hour=15":
                    room_dict['G3-8']['3'].append(room[5:])
                elif hour == "hour=18":
                    room_dict['G3-8']['4'].append(room[5:])
        result['info'] = room_dict
        return result
    else:
        error["reason"] = "invalid region"
        return error


def get_user_info(cookie):  # 获取用户信息（主要是name和ID）, 需要cookie
    handle_url = "http://metalib.lib.whu.edu.cn/pds?func=Bor-info"
    try:
        info_request = urllib2.Request(
            "http://metalib.lib.whu.edu.cn/pds?func=bor-info")
        info_request.add_header('Cookie', cookie)
        root = ET.parse(
            urllib2.urlopen(info_request, timeout=4)).getroot()  # 获取根节点
        name = root.getiterator("name")[0].text.encode('utf-8')
        ID = root.getiterator("id")[0].text.encode('utf-8')
    except Exception, e:
        error["reason"] = e
        return error
    else:
        result['info'] = name,ID
        return result


# 需要cookie
def order_by_room(cookie, sid, name, ID, room, time, day=now.day, month=now.month, year=now.year):
    roomid = None
    try:
        handle_url = 'http://reserv.lib.whu.edu.cn/edit_entry_handler.php'
        postdata = {
            'name': name,
            'description': 'description',
            'start_day': day,
            'start_month': month,
            'start_year': now.year,
            'start_seconds': str((4.5+int(time)*3.5)*3600),
            'all_day': 'no',
            'end_day': day,
            'end_month': month,
            'end_year': year,
            'end_seconds': str((4.5+int(time)*3.5)*3600+12600),
            'rooms[]': room,
            'type': 'I',
            'confirmed': '1',
            'f_bor_id': sid,
            'f_entry_tel': 'tel',
            'f_entry_email': 'email',
            'f_entry_person1': '',
            'f_entry_person2': '',
            'f_entry_person3': '',
            'returl': 'http://reserv.lib.whu.edu.cn/day.php?year=%s&month=%s&day=%s' % (year, month, day),
            'create_by': ID,
            'rep_id': '0',
            'edit_type': 'series'
        }
        order_request = urllib2.Request(
            url=handle_url, data=urllib.urlencode(postdata))
        order_request.add_header('Cookie',  cookie)
        soup = BeautifulSoup(urllib2.urlopen(order_request, timeout=4), 'lxml')
        pageinfo = str(soup)
        # print pageinfo
    except Exception, e:
        error["reason"] = e
        return error
    else:
        if 'Fatal error' in pageinfo:
            error["reason"] = "Fatal error"
            return error
        elif 'repeat reservation' in pageinfo:
            error["reason"] = "repeat reservation"
            return error
        elif 'have not supplied a value for the mandatory field' in pageinfo:
            error["reason"] = "datafield required"
            return error
        elif 'The new booking will conflict with the following entries' in pageinfo:
            error["reason"] = "new booking will conflict with other"
            return error
        else:  # 以下代码为获取预订的房间id
            links = soup.find_all(
                'a', attrs={'href': re.compile('view_entry')})  # 抓取已预订的房间链接
            # str                 # 将gb2312编码为utf-8
            for link in links:
                if link.renderContents() == name:
                    roomid = re.search(
                        r"id=\d+", link['href']).group()[3:]  # 正则匹配出id
            if roomid:
                result["info"] = roomid
                return result
            else:
                error["reason"] = 'unknow error'
                return error


def cancel(cookie, roomid):
    handle_url = "http://reserv.lib.whu.edu.cn/del_entry.php?id=%s" % (
        roomid)
    req = urllib2.Request(url=handle_url)
    req.add_header('Cookie',  cookie)
    try:
        result_soup = BeautifulSoup(
            urllib2.urlopen(req, timeout=4), 'lxml')
        pageinfo = str(result_soup)
    except Exception, e:
        error["reason"] = e
        return error
    else:
        if 'do not have access' in pageinfo:
            error["reason"] = "do not have access to cancle"
            return error
        elif 'Go To Today' in pageinfo:
            result['info'] = roomid
            return result  # 取消预约成功，返回房间ID
        else:
            error["reason"] = "unknow error"
            return error

if __name__ == '__main__':
    # cookie = getcookie('2013302480033', '114028')['info']
    # print cookie
    # userinfo = getuserinfo(cookie)
    # name, ID = userinfo[0], userinfo[1]
    print get_room_info('1', '')
    # order_result = order_by_room(
    #     cookie, '2013302480033', name, ID, '38', '3', '10', '12')
    # print order_result
    # print cancel(cookie, order_result['info'])
