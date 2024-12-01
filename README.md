## BUSHIROAD ONLINE SHOP SCRIPT
#### 功能简介
- 监控商品在库情况变化（目前设置为武藏野Roselia场贩）
- 启动时在所在目录下打印目前在库情况
- 有商品补货时通过桌面通知提醒用户
- 有商品补货时自动将该商品加入购物车，数量默认为1点，并打开购物车网页
#### 用法简介
- 每次启动程序请输入默认浏览器对应的cookie
- 然后挂着就行
- 有Python环境的话可以用.py file, 如果没有可以直接用\dist目录下的exe
#### cookie获取教程
- 进入 https://bushiroad-store.com/cart
- F12, 切换到Network（网络）视图后刷新（F5）
- 在Fetch/XHR中找到**cart.json**
- 选中后, 查看Headers, 下拉到Request Headers一栏
- 找到Cookie, 将其复制, 运行脚本后键入终端并回车即可
