# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from urllib import parse
import os
import json
import base64
import time

def main():
    try:
        config = getConfig() # 설정 파일 가져오기
        AutoExit = config['AutoExit'] # 자동 종료 설정 여부 가져오기
        Headless = config['Headless'] # Headless 설정 여부 가져오기
        if(Headless == "True"): # Headless 모드 동작
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")
        else:
            options = None
        driver = getDriver(options) # 크롬 드라이버 로드
        id = base64.b64decode(config['userId']) # id, pw의 base64 decode
        id = id.decode("UTF-8")
        pw = base64.b64decode(config['userPw'])
        pw = pw.decode("UTF-8")
        driver.get('https://www.ppomppu.co.kr/zboard/login.php')
        loginPpomppu(driver, id, pw) # 뽐뿌 로그인
        time.sleep(1)
        driver.get("http://www.ppomppu.co.kr/zboard/zboard.php?id=humor") # 유머/감동 게시판 이동
        print("LOG : 유머/감동 게시판 이동 성공")
        listVspacePaser(driver) # 글 목록 찾기
        getConfigComment() # 댓글 목록 가져오기
        writeComment(driver,0,list_vspace) # 댓글 작성
        driver.quit()
    except Exception as e:
        print('LOG: Error [%s]' % (str(e)))
    else:
        print("LOG: Main Process in done.")
    finally:
        if(AutoExit == "False"): # 자동 종료가 아니라면
            os.system("Pause")

def getDriver(options=None):
    driver = webdriver.Chrome("chromedriver.exe", options=options)
    driver.implicitly_wait(3)
    print("LOG: Chrome 드라이버 로딩 성공")
    return driver

def getConfig():
    try:
        with open('config.json') as json_file:
            json_data = json.load(json_file)
    except Exception as e:
        print('LOG: Error in reading config file, {}'.format(e))
        return None
    else:
        return json_data

def getConfigComment():
    global commentList
    commentFile = open("config_comment.txt", "r", encoding='UTF8')
    lines = commentFile.readlines()
    lines = list(map(lambda s: s.strip(), lines))
    commentFile.close()
    commentList = lines
    print("LOG: commentList 가져오기 성공")

def loginPpomppu(driver, id, pw):
    WebDriverWait(driver,1000).until(EC.presence_of_element_located((By.XPATH, "//*[@id='user_id']"))).send_keys(id) #찾을때까지 기다림
    driver.find_element_by_xpath("//*[@id='password']").send_keys(pw)
    driver.find_element_by_class_name("log_btn").click()
    
    print("LOG : 로그인 성공")

def listVspacePaser(driver):
    try:
        global list_vspace
        list_vspace = driver.find_element_by_xpath("/html/body/div[6]/div[2]/div[4]/div[1]/table[2]/tbody/tr[8]/td[1]").text # 매크로 실행 시작 기준 최 상단 글 파싱
        list_vspace = int(list_vspace) # 숫자로 변환
        print("LOG : 매크로 시작 글 번호 : %d"%list_vspace)
        return True
    except NoSuchElementException:
        print("LOG : 목록 조회 실패")
        return False

def writeComment(driver,i,list_vspace):
    try:
        temp = 0
        while True:
            print("매크로 동작 횟수 : %d"%i)
            print("%d 번째 댓글을 작성합니다"%(i+1))
            url = "http://www.ppomppu.co.kr/zboard/zboard.php?id=humor&page=1&divpage=73&no=%d"%list_vspace
            driver.get(url)
            i += 1
            time.sleep(3)
            editorFrame = driver.find_element_by_css_selector('.cheditor-editarea-wrapper iframe')
            driver.switch_to_frame(editorFrame)
            editor = driver.find_element_by_xpath("/html/body")

            commentSize = len(commentList)
            if(temp >= commentSize):
                temp = 0
            editor.send_keys(commentList[temp])
            print("------------------------------------------------")
            print("LOG : 댓글 [%s] 입력"%commentList[temp])
            print("------------------------------------------------")
            temp += 1
            driver.switch_to_default_content()
            time.sleep(3)
            driver.find_element_by_xpath("//*[@id='comment_write_form']/tbody/tr[1]/td[2]/table/tbody/tr[4]/td[2]/input[1]").click() #기다림이 좀 필요함
            time.sleep(2)
            print("LOG : 댓글작성 성공")
            time.sleep(2)
            print(" ")
            print(" ")
            time.sleep(2)
            print(" ")
            print(" ")
            list_vspace -= 1
            time.sleep(70)
        return True
    except:
        try:
            alert = driver.switch_to_alert()
            message = alert.text
            alert.accept()
        except:
            print("LOG : 댓글 작성 실패")
            print("LOG : %s"%message)
            driver.get("http://www.ppomppu.co.kr/zboard/zboard.php?id=humor")
            writeComment(driver,i,list_vspace)

if __name__ == '__main__':
    main()
