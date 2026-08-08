
---docker 使用说明---
https://cxykk.com/?p=231


网络端口映射
docker run 命令创建容器时添加端口映射的方法有两种： -P ( 大写的 P ) 和 -p (小写的 p )

这两种方法的区别是：

1、 **-P:**是容器内部端口随机映射到主机的高端口；
2、 **-p:**是容器内部端口绑定到指定的主机端口；
    要指定映射到某个端口，则可以使用 -p [port]:[port] 参数
    要绑定 udp 协议端口，只能使用 -p 参数，且在最后添加 /udp 字符串
     docker run -d -p 127.0.0.1:5553:5000/udp jcdemo/flaskapp
     使用 docker port 命令查看某个容器的端口绑定情况
     多次使用 -p 参数可以映射多个端口
    - docker run -it -p 3306:3306 -p 33060:33060 --name mysqlServer -e MYSQL_ROOT_PASSWORD=Good2017! -d mysql:tag

     - docker run -it -p 8088:8088   --name web-ubuntu -v D:/tmp:/tmp ubuntu bash

共享主机文件夹     
  - docker run -it --name="U1"  -v D:/git/rong.plus/cppblog:/mycpp ubuntu bash
    -v 共享主机文件夹
    
在Container运行命令:
    - docker exec -it ymwx-mysql bash