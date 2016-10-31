# WebChat
这是一个用于学习目的的Python聊天室应用,目前版本为1.0

## 注意：
此项目仅用于学习目的，有很多 bug，且作者已停止维护，请谨慎使用！！！！！

登陆界面:

![login](https://geekpics.net/images/2015/04/19/iroQvOj.png)

聊天室界面:

![room](https://geekpics.net/images/2015/04/19/rYNVLjh.png)


大体架构:
* 后端框架使用flask框架.我写这个应用主要出于学习目的,flask是轻量级的框架,相比于我之前尝试过的Rails来说,我认为我学习到了更本质的东西,Rails的抽象程度过高.
* 后端数据存储使用了mongoDB和Redis.储存用户信息使用了mongoDB,储存聊天记录和聊天室信息使用了Redis.主要考虑到并没有将这些信息组织成表的需求,而且使用NoSQL数据库随时可以轻松修改文档结构,非常方便.使用Redis主要因为Redis更偏重内存数据存储,聊天记录的更新速度较高,而且Redis的内置数据结构更丰富.
* 发送验证邮件使用了Celery任务队列,中间层使用了RabbitMQ.
* 实时通信部分使用socket.io库和相对应的flask-socketio插件.目前实时通信的主要实现有ajax长轮询/iframe stream/websocket三种,整体技术演进过程请参考[这一系列文章](http://www.ibm.com/developerworks/cn/views/web/libraryview.jsp?sort_by=&show_abstract=true&show_all=&search_flag=&contentarea_by=Web+development&search_by=%E5%8F%8D%E5%90%91+Ajax+%E9%83%A8%E5%88%86&topic_by=-1&type_by=%E6%89%80%E6%9C%89%E7%B1%BB%E5%88%AB&ibm-search=%E6%90%9C%E7%B4%A2).相比之下websocket最为高效,然而兼容性却比较差.所以.我最终选用了socket.io库来实现这个应用,socket.io库提供了一层封装,在不同兼容性的浏览器下会使用不同的策略来实现实时通信,在支持websocket的浏览器上自然会使用websocket.
* 前端使用了bootstrap和jQuery.通过这个小项目我意识到了全栈的重要性,即使是后端工程师在搭建原型的过程中也需要简单的前端知识.这次我对DOM树有了更多的理解,同时对jQuery也入了门.

安装:
* `git clone https://github.com/choleraehyq/WebChat.git`
*   建立virtualenv隔离环境,比如`virtualenv venv && source venv/bin/activate`
*   安装依赖 `cd WebChat && pip install -r requirement.txt`
*   确保RabbitMQ/MongoDB/Redis已安装并正常启动
*   开启celery任务队列`celery -A application.celery worker --loglevel=info`
*   另起一个终端,在项目目录下执行`python manage.py runserver`启动
*   使用浏览器访问127.0.0.1:5000即可

TODO:
* 用户列表中出现undefined用户的情况.
* 还没有实现REST架构的API.
* 对使用Gunicorn进行部署,Nginx做反向代理还不熟悉.
* 前端有待改进. 
* 加入使用其他账号登陆的功能(Google/Github/Weibo)


