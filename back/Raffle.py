import requests
import json
import sys
import time
import math
import re
import random
from random import choice

print('B站在线动态抽奖工具 v2021.03.18 cj.bili.fan')

try:
    typ=int(sys.argv[1])
    dyid=int(sys.argv[2])
    HJNUM=int(sys.argv[3])
except:
    print('传入的参数不正确！')
    sys.exit()

def gzlisturl(page):
    return 'https://api.bilibili.com/x/relation/followers?vmid='+str(myuid)+'&pn='+str(page)

def likelisturl(page):
    return 'https://api.vc.bilibili.com/dynamic_like/v1/dynamic_like/spec_item_likes?dynamic_id='+str(dyid)+'&pn='+str(page)

def repBool(value):
    if value:
        val=str(value).replace('True','√')#✔
    else:
        val=str(value).replace('False','X')#❌
    return val

def gethtml(url, header):
    i = 0
    while i < 3:
        try:
            html = requests.get(url, headers=header, timeout=5)
            html.encoding = "utf-8"
            return html.text
        except requests.exceptions.RequestException:
            print('警告：超时'+str(i+1)+'次，位于'+str(errortime)+'页')
            i += 1

def now_time():
    t = time.strftime("%Y%m%d%H%M%S", time.localtime())
    return t

def _get_offset(data_json):
    if 'offset' in data_json['data']:
        return data_json['data']['offset']
    else:
        return None

def getZF(dyn_id):
    print('尝试获取完整转发列表……')
    dynamic_api = "https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost_detail"
    info = {
        "time": now_time(),
        "dyn_id": dyn_id
    }
    header={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/88.0.4324.182 Safari/537.36",
    }
    # 首次数据获取
    offset = "1:0"
    param = {'dynamic_id': dyn_id, 'offset': offset}
    data = requests.get(dynamic_api, headers=header, params=param, timeout=10)
    data_json = json.loads(data.text)
    total_num = data_json['data']['total']
    info['total'] = total_num
    #print("总转发人数：" + str(total_num))

    # 获取全部数据
    uidall=[]
    now_num = 0
    count = 0
    users = []
    while now_num < total_num:  # 循环获取页面
        param = {'dynamic_id': dyn_id, 'offset': offset}
        data = requests.get(dynamic_api, headers=header, params=param, timeout=10)
        data_json = json.loads(data.text)
        for i in range(0, 20):  # 获取单页的所有用户（最多20条）
            if count < total_num:
                count += 1
                try:
                    uid = data_json['data']['items'][i]['desc']['uid']
                    uidall.append(uid)
                except:
                    pass
            else:  # 最后一页数量少于20时
                break
        offset = _get_offset(data_json)
        if offset is None:
            break
        now_num += 20
        time.sleep(0.2)
    uidall.sort()
    try:
        uidall.remove(myuid)
    except:
        pass
    print('完成，共有 '+str(len(uidall))+' 位，已存至数组中')
    return uidall

def getPL(Dynamic_id):
    print('尝试获取完整评论列表……')
    current_page = 1
    header={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/86.0.4324.182 Safari/537.36",
    }
    DynamicAPI = "https://api.live.bilibili.com/dynamic_repost/v1/dynamic_repost/view_repost?dynamic_id=" + Dynamic_id + "&offset=0"
    r = gethtml(DynamicAPI,header)
    json_data = json.loads(r)
    href = json_data['data']['comments'][0]
    rid = href['detail']['desc']['origin']['rid']
    link1 = 'https://api.bilibili.com/x/v2/reply?&jsonp=jsonp&pn='
    link2 = '&type=11&oid='
    link3 = '&sort=2&_=1570498003332'
    comment_list = []
    userlist_1=[]
    pool = {}
    r = gethtml(link1 + str(current_page) + link2 + str(rid) + link3, header)
    json_data = json.loads(r)
    if json_data['code']==-404:
        print('获取评论失败/此动态没有除UP主自己的评论以外的评论！')
        sys.exit()
    if json_data['code']==-412:
        print('获取评论失败，调取间隔过短，请稍后重试！')
        sys.exit()
    comments_num = json_data['data']['page']['count']
    pages_num = comments_num // 20 + 1

    while True:
        r = gethtml(link1 + str(current_page) + link2 + str(rid) + link3, header)
        json_data1 = json.loads(r)

        if json_data1['data']['replies']:
            for reply in json_data1['data']['replies']:
                userlist_1.append(int(reply['member']['mid']))
        current_page += 1
        if current_page > pages_num:
            break
    userlist_1.sort()
    try:
        userlist_1.remove(myuid)
    except:
        pass
    print('完成，共有 '+str(len(userlist_1))+' 位，已存至数组中')
    return userlist_1

def getDZ(dyid):
    global errortime
    print('尝试获取完整点赞列表……')
    header={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/88.0.4324.182 Safari/537.36",
    }
    r=gethtml(likelisturl(1),header)
    errortime=1
    userlist_dict=json.loads(r)
    jdata=userlist_dict['data']
    jlist=jdata['item_likes']
    totalfans=jdata.get('total_count')
    math2=math.ceil(jdata.get('total_count')/20)*20-totalfans
    pages=math.ceil(totalfans/20)
    times=1
    errortime=1
    userlist_1=[]
    while times < pages+1:
        errortime=times
        r=gethtml(likelisturl(times), header)
        userlist_dict=json.loads(r)
        jdata=userlist_dict['data']
        jlist=jdata['item_likes']
        times2=0
        if times != pages:
            while times2<20:
                userlist_1.append(jlist[times2].get('uid'))
                times2=times2+1
        else:
            while times2<20-math2:
                userlist_1.append(jlist[times2].get('uid'))
                times2=times2+1
        times=times+1
        time.sleep(0.3)
    #print(userlist_1)
    userlist_1.sort()
    try:
        userlist_1.remove(myuid)
    except:
        pass
    print('完成，共有 '+str(len(userlist_1))+' 位，已存至数组中')
    return list(userlist_1)

def getGZ():
    global errortime
    print('尝试获取完整粉丝列表……')
    header={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/88.0.4324.182 Safari/537.36",
    "Cookie":cookie,
    }
    r=gethtml(gzlisturl(1),header)
    errortime=1
    userlist_dict=json.loads(r)
    jdata=userlist_dict['data']
    jlist=jdata['list']
    totalfans=jdata.get('total')
    math2=math.ceil(jdata.get('total')/50)*50-totalfans
    pages=math.ceil(totalfans/50)
    times=1
    errortime=1
    userlist_1=[]
    while times < pages+1:
        errortime=times
        r=gethtml(gzlisturl(times), header)
        userlist_dict=json.loads(r)
        jdata=userlist_dict['data']
        jlist=jdata['list']
        times2=0
        if times != pages:
            while times2<50:
                userlist_1.append(jlist[times2].get('mid'))
                times2=times2+1
        else:
            while times2<50-math2:
                userlist_1.append(jlist[times2].get('mid'))
                times2=times2+1
        times=times+1
        time.sleep(0.3)
    userlist_1.sort()
    print('完成，共有 '+str(len(userlist_1))+' 位，已存至数组中')
    return list(userlist_1)

def getname(users):
    times=0
    while times<len(users):
        url='https://api.bilibili.com/x/space/acc/info?mid='+str(users[times])
        header={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/88.0.4324.182 Safari/537.36",
        }
        res = requests.get(url=url,headers=header)
        resback=json.loads(res.text)
        usrinfo=resback.get('data')
        try:
            mid=usrinfo.get('mid')
            uname=usrinfo.get('name')
        except:
            mid=(users[times])
            uname='[获取失败]'
        print(str(times+1)+' '+uname+' (UID:'+str(mid)+')')
        times=times+1

#程序开始运行
TGZ=False
TZF=False
TPL=False
TDZ=False
LBGZ=[]
LBZF=[]
LBPL=[]
LBDZ=[]
errortime=1
isLogin=False
if typ>=8 and typ<=15:
    TGZ=True
if (typ % 2) != 0 and typ<=15:
    TZF=True
pltemp=[2,3,6,7,10,11,14,15]
if typ in pltemp:
    TPL=True
dztemp=[4,5,6,7,12,13,14,15]
if typ in dztemp:
    TDZ=True
if not TGZ and not TZF and not TPL and not TDZ:
    print('输入的获奖条件无效！请重新运行程序...')
    sys.exit()
try:
    HJNUM=int(HJNUM)
except:
    print('输入的获奖者数量无效！')
    sys.exit()
if HJNUM<1:
    print('输入的获奖者数量小于1！')
    sys.exit()
TZF2=repBool(TZF)
TPL2=repBool(TPL)
TDZ2=repBool(TDZ)
TGZ2=repBool(TGZ)
print('转发：'+str(TZF2)+' 评论：'+str(TPL2)+' 点赞：'+str(TDZ2)+' 关注：'+str(TGZ2))
if TGZ:
    try:
        cookie=sys.argv[4]
    except:
        print('检测关注需要登录，请在参数里附上cookie！程序即将退出……')
        print('提示：可以前往 t.bili.fan 快速获取到自己的cookie')
        sys.exit()
    print('尝试使用预设的cookie进行模拟登录……')
    header={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/88.0.4324.182 Safari/537.36",
    "Cookie":cookie,
    }
    r=requests.get('http://api.bilibili.com/x/space/myinfo',headers=header).text
    userinfo_dict=json.loads(r)
    try:
        jdata=userinfo_dict['data']
        myuid=jdata.get('mid')
        name=jdata.get('name')
        level=jdata.get('level')
        coins=jdata.get('coins')
        print('模拟登录成功，UID：'+str(myuid)+'，用户名：'+name+'，等级 '+str(level)+'，拥有 '+str(coins)+' 枚硬币')
        isLogin=True
    except:
        print('模拟登录失败！可能是cookie过期或未登录，程序即将退出……')
        sys.exit()

#dyid=input('输入动态ID：')
if TGZ and not TZF and not TPL and not TDZ:
    print('当前选择的是直接从粉丝列表里抽，将不会使用任何动态数据')
    dyid=0
else:
    dyid=str(dyid)
    print('正在获取动态详情…… 动态ID:',dyid)
    try:
        header={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/88.0.4324.182 Safari/537.36",
        }
        url='https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id='+dyid
        res = requests.get(url=url,headers=header)
        resback=json.loads(res.text)
        dyinfo=resback.get('data')
        if TGZ and dyinfo.get('card').get('desc').get('user_profile').get('info').get('uid')!=myuid:
            print('动态发送者（'+dyinfo.get('card').get('desc').get('user_profile').get('info').get('uname')+'）和当前已登录用户不一致，无法检测是否已关注！即将退出……')
            sys.exit()
        tmstmp=time.localtime(dyinfo.get('card').get('desc').get('timestamp'))
        print('------------------------------------------------------------')
        print('动态发送者：'+str(dyinfo.get('card').get('desc').get('user_profile').get('info').get('uname'))+'\n浏览：'+str(dyinfo.get('card').get('desc').get('view'))+'，转发：'+str(dyinfo.get('card').get('desc').get('repost'))+'，评论：'+str(dyinfo.get('card').get('desc').get('comment'))+'，点赞：'+str(dyinfo.get('card').get('desc').get('like')))
        print('发送时间：'+time.strftime("%Y-%m-%d %H:%M:%S", tmstmp))
        print('------------------------------------------------------------')
    except:
        SHEXIT=False
        try:
            if TGZ and dyinfo.get('card').get('desc').get('user_profile').get('info').get('uid')!=myuid:
                SHEXIT=True
        except:
            pass
        if SHEXIT:
                sys.exit()
        print('获取出错，可能是动态ID输入有误，请检查后重试')
        sys.exit()
    if not isLogin:
        myuid=dyinfo.get('card').get('desc').get('user_profile').get('info').get('uid')
    print('准备开始抽取……（抽取时将自动过滤UP主自己和重复转发/评论的用户）')
    if dyinfo['card']['desc']['repost']>575:
        print('警告：转发数量超过575的部分无法被统计！')
    print('')
    Error=False
    if TZF and dyinfo['card']['desc']['repost']==0:
        print('这条动态没有任何用户转发！')
        Error=True
    if TPL and dyinfo['card']['desc']['comment']==0:
        print('这条动态没有任何用户评论！')
        Error=True
    if TDZ and dyinfo['card']['desc']['like']==0:
        print('这条动态没有任何用户点赞！')
        Error=True
    if Error:
        sys.exit()
LBALL=[]
if TZF:
    LBZF=getZF(dyid)
    #print(LBZF)
    if len(LBALL)!=0:
        LBALL=set(LBALL)&set(LBZF)
    else:
        LBALL=set(LBZF)
#print('1--'+str(len(LBZF)))
if TPL:
    LBPL=getPL(dyid)
    #print(LBPL)
    if len(LBALL)!=0:
        LBALL=set(LBALL)&set(LBPL)
    else:
        LBALL=set(LBPL)
#print('2--'+str(LBALL))
if TDZ:
    LBDZ=getDZ(dyid)
    #print(LBDZ)
    if len(LBALL)!=0:
        LBALL=set(LBALL)&set(LBDZ)
    else:
        LBALL=set(LBDZ)
#print('3--'+str(LBALL))
if TGZ:
    LBGZ=getGZ()
    #print(LBGZ)
    if len(LBALL)!=0:
        LBALL=set(LBALL)&set(LBGZ)
    else:
        LBALL=set(LBGZ)
#print(LBALL)
print('\n已获取到符合要求的参与者数量为：'+str(len(list(LBALL))))

if HJNUM>len(list(LBALL)) or HJNUM<1:
    print('输入的获奖者数量（'+str(HJNUM)+'）超出范围！')
    sys.exit()
HJMD=[]
times=1
while True:
    while True:
        HJuser=choice(list(LBALL))
        if not HJuser in HJMD:
            HJMD.append(HJuser)
            times=times+1
        break
    if times>HJNUM:
        break
    #print(HJNUM,times,HJMD)
HJMD.sort()
random.shuffle(HJMD)
print('抽取完成，以下为获奖用户名单：')#+str(HJMD))
print('-----------------------------------')
getname(HJMD)
print('-----------------------------------')
print('程序即将退出……')
sys.exit()
