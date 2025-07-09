## 项目介绍：
一个基于华为openGauss和Flask实现的超市商品进销存管理系统，实现的功能如下：
1.角色管理（三种不同角色具有不同权限）
2.商品管理（商品的增删改查）
3.员工管理（销售采购员工的增删改查）
4.销售采购（销售采购记录的增删改查+可视化）

## 数据库开启步骤：
在本地电脑的服务管理器中开启 VMWare NAT Service 和 VMWare DHCP Service 服务，
开启虚拟机和 finalshell，二者连接成功后在 finalshell 里输入 su omm 切换到 omm用户，
然后运行 gs_om -t start 开启 openGauss 服务，再运行 gsql -p 26000 -U remote_user -W "替换为实际密码"
登录数据库，再运行 \c supermarket_db 切换到 supermarket_db 数据库下即可开始操作。

## 项目运行步骤：
打开当前目录终端，执行 venv\Scripts\activate
python main.py，打开对应服务器地址即可

## 数据库文件保存步骤：
然后在omm用户下运行 gs_dump -U remote_user supermarket_db -f /home/songxip/Desktop/supermarket_db_backup.sql
可导出数据库文件到虚拟机桌面上，将文件复制粘贴到本地即可

## 项目说明：
1.管理员仅一个（不支持添加）
2.管理员账号：admin（不支持修改）；管理员初始密码：123456
3.采购员和销售员用户名（不支持修改）：其id编号（不支持修改）；采购员和销售员的初始密码：123456
4.采购员的id编号：统一为PExxx；销售员的id编号：统一为SExxx；顾客的id编号：统一为Cxxx
