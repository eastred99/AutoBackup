#coding=utf-8

import configparser,sys,os,time,zipfile

mysql_usr =''
mysql_pwd =''
mysql_db =''
mysql_charset ='gbk'
backup_path   ='backup'
cmd_path =''
Logs_path = 'logs'
backup_time='02'
keep=10
zip_source_path=''
zip_destination_path=''

def ini_get():
    global mysql_usr
    global mysql_pwd
    global mysql_db
    global mysql_charset
    global backup_path
    global cmd_path
    global Logs_path
    global backup_time
    global keep
    global zip_source_path
    global zip_destination_path
    config = configparser.ConfigParser()
    config.readfp(open("config.ini"))
    mysql_usr =config.get("settings","mysql_usr")
    mysql_pwd =config.get("settings","mysql_pwd")
    mysql_db =config.get("settings","mysql_db")
    mysql_charset =config.get("settings","mysql_charset")
    backup_path   =config.get("settings","backup_path")
    cmd_path =config.get("settings","cmd_path")
    Logs_path =config.get("settings","Logs_path")
    backup_time=config.get("settings","backup_time")
    keep=int(config.get("settings","keep"))
    zip_source_path=config.get("settings","zip_source_path")
    zip_destination_path=config.get("settings","zip_destination_path")
            
def writeLogs(filename,contents):
    f = open(filename,'a')
    f.write(contents)
    f.close()
    
def backup():
    fname = backup_path + os.sep + time.strftime('%Y%m%d_%H%M%S') + '.sql'
    # 创建当日备份目录
    if not os.path.exists(backup_path):
        Msg = '-'*30 + time.strftime('%Y-%m-%d,%H:%M:%S') + '-'*30 + '\n'
        if(os.mkdir(backup_path)) == None:
            Msg += '** 成功创建备份目录： ' + backup_path + '\n\n'
            writeLogs(Logs_path,Msg)
        else:
            Msg += '!! 创建备份目录： ' + backup_path + '失败，请检查目录是否可写！\n\n'
            writeLogs(Logs_path,Msg)
            #sys.exit()
    # 备份 Mysql 命令
    cmd_dump = "%smysqldump -u%s -p%s --default-character-set=%s --opt %s > %s"%(cmd_path,mysql_usr,mysql_pwd,mysql_charset,mysql_db,fname)
    # 执行备份命令
    if os.system(cmd_dump) == 0:
        writeLogs(Logs_path,'数据备份为： ' + fname + '\n')
    else:
        writeLogs(Logs_path,'数据备份失败！\n')

def cleanup():
    dirpath=backup_path
    files = os.listdir(dirpath)
    files.sort(key=lambda x:str(x[:-4]))
    if len(files)>keep:
        for f in files[:-keep]:
            os.remove(dirpath+os.sep+f)

def create_zip_file(zip_source_path,zip_destination_path):
    z=zipfile.ZipFile(zip_destination_path+'.zip','w',zipfile.ZIP_DEFLATED)
    startdir=zip_source_path
    for dirpath,dirnames,filenames in os.walk(startdir):
        for filename in filenames:
            # print(dirpath+':::'+filename)
            z.write(os.path.join(dirpath,filename),os.path.join(dirpath.replace(zip_source_path,''),filename))
    z.close()

if __name__=='__main__':
    # print('\n\r'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'自动备份程序开始运行\n\r问题反馈QQ：599065620')
    print('\n\r{0}，自动备份程序开始运行\n\r使用中如有问题请联系QQ：{1}'.format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'599065620'))
    to_backup=True
    while(True):
        try:
            ini_get()
        except:
            writeLogs(Logs_path,'读取配置文件错误')
        if to_backup and (time.strftime('%H',time.localtime(time.time()))==backup_time):
            try:
                backup()
                create_zip_file(zip_source_path,zip_destination_path)
                to_backup=False
            except:
                writeLogs(Logs_path,'备份数据库错误')
                to_backup=True
                continue
            try:
                cleanup()
                to_backup=False
            except:
                writeLogs(Logs_path,'清除多余备份文件错误')
                to_backup=True
                continue
        else:
            to_backup=True
        time.sleep(1800)
        