from datetime import datetime, timedelta
from credentials import Credentials
from libxduauth import *
from bs4 import BeautifulSoup as bs
import time


class Due(Credentials):
    def __init__(self):
        super().__init__()
        self.place_id = 541  # 羽毛球场地基准号541 ( 当场地号小于10时 )
        self.place_id_10more = 480  # 大于等于10 ( 当场地号大于等于10时 )
        self.pingpang_place_id = 532  # 乒乓球场地基准号532
        self.day = datetime.today()  # 默认为今天
        self.start_time = ""
        self.end_time = ""

        # urls
        self.url = "http://tyb.meetingcn.org"
        self.url_order = self.url + "/index/order_post"
        self.url_checkorder = self.url + "/index/my_order"
        self.url_cancel = self.url + "/index/cancel_order"

        # 登录
        try:
            self.s = IDSSession('', self.IDS_USERNAME, self.IDS_PASSWORD)
            slogin = self.s.is_logged_in()
            if slogin:
                print("登陆成功")
                self.cookies = self.s.cookies
            else:
                print("登陆失败")
        except:
            print("登陆出错")
            exit(-1)

        # 获取可定场地的字典
        self.dic = self.find_empty()

    # 订场
    def get_due(self, days=1, start=18, end=20):
        due_list = self.find_place(days, start, end)
        place = 0

        if days == 2:
            self.day = (self.day + timedelta(days=1)).strftime("%Y-%m-%d ")
        elif days == 3:
            self.day = (self.day + timedelta(days=2)).strftime("%Y-%m-%d ")
        else:
            self.day = self.day.strftime("%Y-%m-%d ")

        self.start_time = self.day + str(start) + ":00"
        self.end_time = self.day + str(end) + ":00"

        if len(due_list):
            print("已经为你选择第 " + str(due_list[0]) + " 号场地")
            place = due_list[0]
        else:
            print("该时间段没有场地可用了~")
            exit(-1)

        if place < 10:
            self.place_id = str(self.place_id + place)
        else:
            self.place_id = str(self.place_id_10more + place)

        data_due = {
            "phone": self.phone,
            "stu_name_1": self.stu_name_1,
            "stu_id_1": self.stu_id_1,
            "stu_name_2": self.stu_name_2,
            "stu_id_2": self.stu_id_2,
            "place_id": self.place_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }
        try:
            self.s.post(self.url_order, data=data_due, cookies=self.cookies)
            print("正在预约中...")
            time.sleep(5)
            if self.check_due():
                print("预定成功")
                print(self.check_due(msg=True))
            else:
                print("预定失败")
        except:
            print("预定失败")

    # 取消预定
    def cancel_due(self):
        html = self.s.get(self.url_checkorder, cookies=self.cookies).text
        soup = bs(html, 'html.parser')
        index = soup.find('tr', {'class': 'border-top'}).findAll("td")[0].text
        check = soup.find('tr', {'class': 'border-top'})
        lists = check.findAll('td')
        params = {
            "order_id": index
        }
        try:
            self.s.get(self.url_cancel, params=params, cookies=self.cookies)
            print("取消" + index + "号订单 : " + lists[5].text)
        except:
            print("取消预定出错")
        print("正在取消中...")
        time.sleep(3)
        if not self.check_due():
            print("取消成功")
        else:
            print("取消出错")

    # 检查预定成功与否
    def check_due(self, msg=False) -> bool:
        html = self.s.get(self.url_checkorder, cookies=self.cookies).text
        soup = bs(html, 'html.parser')
        check = soup.find('tr', {'class': 'border-top'})
        lists = check.findAll('td')
        check = str(check)
        if check.find("已取消") and check.find("已过期") == -1:
            if msg:
                print("已经预定" + lists[5].text + " 时间为 " + lists[6].text)
            return True
        else:
            if msg:
                print("当前没有预定场地")
            return False

    # 寻找空场地
    def find_empty(self) -> dict:
        print("正在获取可用场地")
        html = self.s.get(self.url, cookies=self.cookies).text
        soup = bs(html, 'html.parser')
        emptyplace = soup.find('tbody').findAll('div', {'data-place_id': True})
        dic = {}
        for i in emptyplace:
            # set.add((i.attrs['data-place_id'], i.attrs['data-start_time'], i.attrs['data-end_time']))
            place_id = i.attrs['data-place_id']
            if (place_id in dic):
                dic[place_id].append(i.attrs['data-start_time'])
            else:
                li = []
                li.append(i.attrs['data-start_time'])
                dic[place_id] = li
        return dic

    def find_place(self, days=1, start=18, end=20) -> list:  # 基于find_empty, 查询对应时间段可以预定的场地
        if days == 2:
            day = (self.day + timedelta(days=1)).strftime("%Y-%m-%d ")
            print("明天 " + day)
        elif days == 3:
            day = (self.day + timedelta(days=2)).strftime("%Y-%m-%d ")
            print("后天 " + day)
        else:
            day = self.day.strftime("%Y-%m-%d ")
            print("今天 " + day)
        print("可以预定的场地如下\n" + "----------------------------------------------------")

        self.start_time = day + str(start) + ":00"
        self.end_time = day + str(end) + ":00"
        candue = False
        due_place = []
        for due_id, due_time in self.dic.items():
            due_id = int(due_id)
            flag = True
            for i in range(start, end):  # 字典存的都是开始的时间, 故不用end+1
                flag = flag and ((day + str(i) + ":00") in due_time)
            if flag:
                candue = True
                if due_id > 510:
                    print(str(due_id - self.place_id) + "号场可以预定, 时间" + self.start_time + "到" + self.end_time)
                    due_place.append(due_id - self.place_id)
                else:
                    print(str(due_id - self.place_id_10more) + "号场可以预定, 时间" + self.start_time + "到" + self.end_time)
                    due_place.append(due_id - self.place_id_10more)
        # if not candue:
        #     print("没有该时段的场地可以预定了哦~")
        due_place.sort()
        return due_place  # 返回可以预定场地号的曾序列表
