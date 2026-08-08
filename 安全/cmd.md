netstat -ano    -- 列举端口
tasklist /FI "PID eq 27492"   -查看进程信息
netstat -natp
taskkill /pid 11704 /F  杀死进程


services.msc
lusrmgr.msc 用户

择开始 > 运行，输入 msconfig，

1.1.4 选择开始 > 运行，输入 regedit，打开注册表，查看开机启动项是否正常，特别注意如下三个注册表项：
HKEY_CURRENT_USER\software\micorsoft\windows\currentversion\run
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Runonce

删除共享

net share c$ /delete

net share d$/delete

net share ipc$/delete

net share admin$ /delete

Win+R键调出“运行”，输入“mrt”， 恶意软件清理


>mpcmdrun.exe  -Scan -Scantype 3 -File Temp

tool ---> Windows Firewall Log Analyser 
- nmap - netcat - nessus - wireshark


https://blog.csdn.net/A1100886/article/details/130105345?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522ec0df8f10e8fbc51b9d8751e53faee48%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=ec0df8f10e8fbc51b9d8751e53faee48&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-130105345-null-null.142^v102^pc_search_result_base1&utm_term=%E7%B3%BB%E7%BB%9F%E5%AE%89%E5%85%A8&spm=1018.2226.3001.4449

#将非登陆用户的Shell设为/sbin/nologin
usermod -s /sbin/nologin  用户名
 
#锁定长期不使用的账号
usermod -L 用户名
passwd -l  用户名
passwd -S  用户名
 
#删除无用的账号
userdel [-r] 用户名
 
#锁定账号文件passwd shadow
chattr +i /etc/passwd /etc/shadow            #锁定文件
lsattr /etc/passwd /etc/shadow               #查看文件状态
chattr -i /etc/passwd /etc/shadow            #解锁文件
 

 锁定账号文件--chattr命令
 验证文件的完整性,防止文件被篡改--md5sum命令