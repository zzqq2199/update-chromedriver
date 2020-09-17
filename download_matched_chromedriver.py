import winreg
import re
import traceback
import os
DRIVER_CONFIG_PATH = "./driver.json"

version_re = re.compile(r'^[1-9]\d*\.\d*.\d*')

def version_cmp(v1, v2):
    '''
    v1>v2: return 1
    v1==v2:return 0
    v1<v2: return -1
    '''
    l1 = list(map(int, v1.split('.')))
    l2 = list(map(int, v2.split('.')))
    for i in range(min(len(l1),len(l2))):
        if l1[i] < l2[i]: return -1
        if l1[i] > l2[i]: return 1
    if len(l1) < len(l2): return -1
    if len(l1) > len(l2): return 1
    return 0

def get_chrome_version():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
        _v, type = winreg.QueryValueEx(key, 'version')
        print(f'Current Chrome Version: {_v}')
        return _v
    except:
        print(f"check chrome version failed:\n{traceback.format_exc()}")

def get_driver_version(driver_path):
    cmd = fr'{driver_path} --version'
    import subprocess
    try:
        print(f"cmd={cmd}")
        out, err = subprocess.Popen(cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE
        ).communicate()
        out = out.decode('utf-8')
        _v = out.split(' ')[1]
        print(f'Current Chromedriver Version: {_v}')
        return _v
    except:
        print(f"check chromedriver version failed:\n{traceback.format_exc()}")
        return 0
        
def get_matched_chromedriver_version(chrome_version, url):
    import urllib.request
    import urllib.parse
    import zipfile
    rep = urllib.request.urlopen(url).read().decode('utf-8')
    directory = re.compile(r'>(\d.*?/)</a>').findall(rep)
    # print(directory)
    chrome_driver_version = ""
    for dir in directory:
        if version_cmp(dir[:-1],chrome_version)==-1:
            chrome_driver_version = dir[:-1]
    return chrome_driver_version

def donwload_driver(driver_version, url, save_dir):   
    import urllib.request
    import urllib.parse
    import zipfile
    def progress_func(blocknum, blocksize, totalsize):
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100: percent = 100
        downsize = blocknum * blocksize
        if downsize > totalsize: downsize = totalsize
        s = f"{percent:.2f}% ====> {downsize/1024/1024:.2f}M/{totalsize/1024/1024:.2f}M \r"
        import sys
        sys.stdout.write(s)
        sys.stdout.flush()
        if percent == 100:
            print('')
    print(f"save_dir={save_dir}")
    dir_url = urllib.parse.urljoin(url, driver_version+"/")
    down_url = urllib.parse.urljoin(dir_url, 'chromedriver_win32.zip')
    print(f"down_url={down_url}")
    save_path = os.path.join(save_dir, os.path.basename(down_url))
    print(f"save_path={save_path}")
    urllib.request.urlretrieve(down_url, save_path, progress_func)
    zfile = zipfile.ZipFile(save_path, 'r')
    for fileM in zfile.namelist():
        zfile.extract(fileM, os.path.dirname(save_path))
    zfile.close()
    os.remove(save_path)

def check_and_update(chromedriver_path, mirror_url):
    print(f"chromdriver.exe路径：{chromedriver_path}")
    print(f"chromedriver镜像网站：{mirror_url}")
    chrome_version = get_chrome_version()
    current_driver_version = get_driver_version(chromedriver_path)
    print(f"当前Chrome版本号：{chrome_version}")
    print(f"当前chromedriver版本号：{current_driver_version}")
    print(f"查询与Chrome版本号{chrome_version}对应的chromedriver版本号...")
    driver_version = get_matched_chromedriver_version(chrome_version,mirror_url)
    print(f"与当前Chrome版本号{chrome_version}对应的chromedriver版本号为:{driver_version}")
    if driver_version == current_driver_version:
        print(f"chromedriver版本匹配！")
    else:
        print(f"chromedriver版本不匹配！准备下载")
        donwload_driver(driver_version, mirror_url, os.path.split(chromedriver_path)[0])
        print(f"chromedriver版本更新完毕")
        new_driver_version = get_driver_version(chromedriver_path)
        print(f"更新后的chromedriver版本号：{new_driver_version}")
    

if __name__ == '__main__':
    with open(DRIVER_CONFIG_PATH, 'r') as f:
        content = f.read()
        import json
        driver_config = json.loads(content)
    check_and_update(
        driver_config['chromedriver_path'],
        driver_config['mirror_url']
    )

