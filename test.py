import re                           
import time                         
import requests                     
from bs4 import BeautifulSoup
import sqlite3
import urllib
import json
from math import radians, cos, sin, asin, sqrt
import time
import os

jobName = '深度学习'
filterCondition = {'employeesNumber': 200 , 'salary' : 15, 'distance' : 100} 
headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
        'cookie':'t=8PhrsKYhfhfcTfQs; wt=8PhrsKYhfhfcTfQs; \
        sid=sem_pz_bdpc_dasou_title; JSESSIONID=""; \
        Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1526090478, \
        1526090798,1526114945; __c=1526114945; \
        __g=sem_pz_bdpc_dasou_title; \
        __l=l=%2Fwww.zhipin.com%2F%3Fsid%3Dsem_pz_bdpc_dasou_title&r=https%3A%2F%2Fwww.baidu.com%2Fs%3Fwd%3Dboss%25E7%259B%25B4%25E8%2581%2598%26rsv_spt%3D1%26rsv_iqid%3D0x80a67c4200016ad7%26issp%3D1%26f%3D8%26rsv_bp%3D1%26rsv_idx%3D2%26ie%3Dutf-8%26rqlang%3Dcn%26tn%3Dbaiduhome_pg%26rsv_enter%3D1%26oq%3Dqoo%26rsv_t%3D2b5ev7NGtE%252BFwnua%252BSVfGm8f23Ku%252F2qoR4KHkhJQxh%252BavX4Q4ak21DEF%252FVZ7aKFKWu9E%26inputT%3D1886%26rsv_pq%3Dd1f22f9c0001939a%26rsv_sug3%3D10%26rsv_sug1%3D9%26rsv_sug7%3D100%26bs%3Dqoo&g=%2Fwww.zhipin.com%2F%3Fsid%3Dsem_pz_bdpc_dasou_title; \
        lastCity=101010100; __a=89011344.1526090474.1526090487.1526114945.25.3.14.14; \
        Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1526117856'
    } 

if os.path.exists('test.db'):
    os.remove('test.db')
conn = sqlite3.connect('test.db')
cursor = conn.cursor()
cursor.execute("""create table jobinfo(

    companyName varchar(50),

    salary varchar(10),

    companyStatus varchar(50),

    employeesNumber varchar(10),

    address varchar(20),

    distance float(10, 2),
    
    detailUrls text

   )""")
def get_zhaopin(url, filterCondition = filterCondition):
    '''爬取BOSS直聘网，数据岗位'''

    res = requests.get(url, headers=headers)            
    soup = BeautifulSoup(res.text, 'lxml')              

    titles = soup.select('.job-title')                  
    companys = soup.select('.company-text > h3 > a')    
    reds = soup.select('.red')
    webs = soup.select('.info-primary > h3 > a')                       
    company_infos = soup.select('.company-text > p')    
    
    #循环获取的list
    for title, company, red, company_info, web in zip(titles, companys, reds, company_infos, webs):
        #使用正则获取info和company里面的信息
        re_company = re.findall('<p>(.*)<em class="vline"></em>(.*)<em class="vline"></em>(.*)</p>', str(company_info))
        
        jobDetailUrl = 'https://www.zhipin.com/' + web['href']
        detailRequest = requests.get(jobDetailUrl, headers = headers)
        time.sleep(2)
        detailSoup = BeautifulSoup(detailRequest.text, 'html.parser')
        address = detailSoup.select('.location-address')[0].text
        lng, lat = map(float, detailSoup.select('.map-container')[0]['data-long-lat'].split(','))
        distance = getDistance(lat, lng)
        try:
            data = {
                '工作岗位': title.text.strip(),
                '公司名称': company.text.strip(),
                '工资': red.text.strip(),
                '公司类型': re_company[0][0],
                '公司投资': re_company[0][1],
                '公司人数': re_company[0][2],
                '单位地址': address,
                '离家距离': distance,
                '详情网址': jobDetailUrl
            }
        except:
            continue
        sql = ''' insert into  jobinfo  
                (companyName, salary, companyStatus, employeesNumber, address, distance, detailUrls)
                values
                (?, ?, ?, ?, ?, ?, ?)'''
        para = (data['公司名称'], data['工资'], data['公司投资'], data['公司人数'], data['单位地址'], data['离家距离'], data['详情网址'])
        cursor.execute(sql,para)
        conn.commit()
        print('爬到%s的一个%s职位' % (data['公司名称'], data['工作岗位']))
        print('-'*50)
def getDistance(lat, lng, lat0 = 39.848618, lng0 = 116.296933):
    lng, lat, lng0, lat0 = map(radians, [lng, lat, lng0, lat0])  
    dlng = lng - lng0   
    dlat = lat - lat0   
    a = sin(dlat/2)**2 + cos(lat0) * cos(lat) * sin(dlng/2)**2  
    c = 2 * asin(sqrt(a))   
    r = 6371 # 地球平均半径，单位为公里  
    return c * r

#if __name__ == '__main__':
for i in range(1, 999):
    baseUrls = 'https://www.zhipin.com/c101010100/h_101010100/?query=' + jobName + '&page=' + str(i)
    time.sleep(2)
    try:
        get_zhaopin(baseUrls)
    except IndexError:
        print('全部爬取完毕')
conn.close()