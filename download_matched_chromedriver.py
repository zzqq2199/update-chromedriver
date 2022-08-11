"""
@author: zzqq2199
@reference: https://github.com/cgcel/chromedriver_updater/blob/master/chromedriver_updater.py
"""
import winreg
import re
import traceback
import os
import zipfile
import requests
from zq_tools.zq_logger import default_logger as logger

def get_chrome_version():
    """
    通过注册表查找chrome版本号
    """
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
        _v, type = winreg.QueryValueEx(key, 'version')
        logger.info(f'Current Chrome Version: {_v}')
        return _v
    except:
        logger.fatal(f"check chrome version failed:\n{traceback.format_exc()}")

def get_driver_version(driver_path):
    """
    查看给定chromedriver的版本号
    """
    cmd = fr'{driver_path} --version'
    import subprocess
    try:
        logger.debug(f"cmd={cmd}")
        out, err = subprocess.Popen(cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE
        ).communicate()
        out = out.decode('utf-8')
        _v = out.split(' ')[1]
        logger.info(f'Current Chromedriver Version: {_v}')
        return _v
    except:
        logger.warning(f"check chromedriver version failed:\n{traceback.format_exc()}")
        return 0
        
def get_matched_chromedriver_version(chrome_version, url):
    """
    确定与chrome版本对应的chromedriver版本
    在满足前3个分段版本号一致的前提下，下载最新的chromedriver版本
    例如chrome version=104.0.5112.81
    镜像网站上对应满足要求的chromedriver版本号有 104.0.5112.20, 104.0.5112.29, 104.0.5112.79
    则返回104.0.5112.79
    """
    r = requests.get(url, timeout=5)
    result = r.json()
    target_version = ''
    version_list = chrome_version.split('.')[:-1]
    version = '.'.join(version_list)
    # logger.debug(f"result={result}")
    for i in result:
        if version in i['name']:
            if i['type'] == 'dir':
                target_version = i['name']
    target_version = target_version.strip("/")
    assert(target_version!="")
    return target_version
        
def download_driver_from_mirror(driver_version, url, save_dir="."):
    target_download_url = f"{url}/{driver_version}/chromedriver_win32.zip"
    print(f"driver download url = {target_download_url}")
    r = requests.get(target_download_url)

    save_path = os.path.join(save_dir, "chromedriver_win32.zip")
    with open(save_path, "wb") as file:
        print("开始国内源下载...", end="")
        file.write(r.content)
        print("下载完成")
        zipfile.ZipFile(save_path).extractall()
        print("解压完成")

def check_and_update(chromedriver_path, url='https://registry.npmmirror.com/-/binary/chromedriver'):
    chrome_version = get_chrome_version()
    current_driver_version = get_driver_version(chromedriver_path)
    logger.info(f"Current Chrome Version: {chrome_version}")
    logger.info(f"Current ChromeDriver Version: {current_driver_version}")
    matched_driver_version = get_matched_chromedriver_version(chrome_version,url)
    logger.info(f"Matched ChromeDriver Version: {matched_driver_version}")
    if matched_driver_version == current_driver_version:
        logger.info("Current ChromeDriver matches Chrome, No need to update")
    else:
        logger.info(f"Downloading ChromeDriver Version: {matched_driver_version}")
        download_driver_from_mirror(matched_driver_version, url, os.path.split(chromedriver_path)[0])
        new_driver_version = get_driver_version(chromedriver_path)
        logger.info(f"Updated ChromeDriver Version: {new_driver_version}")
    

if __name__ == '__main__':
    check_and_update(
        chromedriver_path=r".\chromedriver.exe",
    )
    