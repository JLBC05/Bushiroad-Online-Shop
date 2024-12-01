import requests
from bs4 import BeautifulSoup
from plyer import notification
import time
from datetime import datetime
import os
import webbrowser
import json

# 代理配置
tunnel = "y298.kdltps.com:15818"
username = "t12370663163991"
password = "wqhwje9h"
proxies = {
    "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
    "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
}

# 配置
URL = 'https://bushiroad-store.com/pages/roselia2024winter'  # 目标商品页面链接
CHECK_INTERVAL = 60  # 每分钟检查一次

cookie = input("请输入购物车的 Cookie：")

# 商品简称双射定义
product_mapping = {
    "【(1)-(1)】Roselia「Stille Nacht, Rosen Nacht」　Tシャツ Mサイズ": "M码短袖T", 
    "【(1)-(2)】Roselia「Stille Nacht, Rosen Nacht」　Tシャツ Lサイズ": "L码短袖T",
    "【(1)-(3)】Roselia「Stille Nacht, Rosen Nacht」　Tシャツ XLサイズ": "XL码短袖T",
    "【(2)】Roselia「Stille Nacht, Rosen Nacht」　ポケット付きマフラータオル": "毛巾", 
    "【(3)】Roselia「Stille Nacht, Rosen Nacht」　ラバーバンド": "手环", 
    "【(4)-(1)】Roselia「Stille Nacht, Rosen Nacht」　アクリルスタンド 湊 友希那": "ykn立牌", 
    "【(4)-(2)】Roselia「Stille Nacht, Rosen Nacht」　アクリルスタンド 氷川紗夜": "sayo立牌", 
    "【(4)-(3)】Roselia「Stille Nacht, Rosen Nacht」　アクリルスタンド 今井リサ": "lisa立牌", 
    "【(4)-(4)】Roselia「Stille Nacht, Rosen Nacht」　アクリルスタンド 宇田川あこ": "ako立牌", 
    "【(4)-(5)】Roselia「Stille Nacht, Rosen Nacht」　アクリルスタンド 白金燐子": "rinko立牌", 
    "【(5)】Roselia「Stille Nacht, Rosen Nacht」　トレーディング缶バッジ【PACK】": "吧唧十个装", 
    "【(6)】Roselia「Stille Nacht, Rosen Nacht」　記念キーホルダー": "布片挂件", 
    "【(7)】Roselia「Stille Nacht, Rosen Nacht」　クリアファイル": "文件袋", 
    "【(8)】Roselia「Stille Nacht, Rosen Nacht」　トレーディングマット缶バッジ【PACK】": "金丝吧唧", 
    "【(9)】Roselia「Stille Nacht, Rosen Nacht」　トレーディングネームチャーム【PACK】": "角色吊坠", 
    "【(10)】BanG Dream!　ローズラインパーカー Roselia": "连帽衫", 
    "【(11)】BanG Dream!　アンティークネックレス Roselia": "项链", 
    "【(12)】Roselia「Stille Nacht, Rosen Nacht」　つながる！記念箔押しフォトパネル": "照片挂画", 
    "【(13)-(1)】Roselia「Stille Nacht, Rosen Nacht」　ミニのぼり＆スタンドセット 湊 友希那": "ykn小旗", 
    "【(13)-(2)】Roselia「Stille Nacht, Rosen Nacht」　ミニのぼり＆スタンドセット 氷川紗夜": "sayo小旗", 
    "【(13)-(3)】Roselia「Stille Nacht, Rosen Nacht」　ミニのぼり＆スタンドセット 今井リサ": "lisa小旗", 
    "【(13)-(4)】Roselia「Stille Nacht, Rosen Nacht」　ミニのぼり＆スタンドセット 宇田川あこ": "ako小旗", 
    "【(13)-(5)】Roselia「Stille Nacht, Rosen Nacht」　ミニのぼり＆スタンドセット 白金燐子": "rinko小旗", 
    "【(14)-(1)】BanG Dream!　ロングTシャツ Lサイズ Roselia": "L码长袖T", 
    "【(14)-(2)】BanG Dream!　ロングTシャツ XLサイズ Roselia": "XL码长袖T", 
    "【(15)-(1)】Roselia「Stille Nacht, Rosen Nacht」法被 湊友希那": "ykn法被", 
    "【(15)-(2)】Roselia「Stille Nacht, Rosen Nacht」法被 氷川紗夜": "sayo法被", 
    "【(15)-(3)】Roselia「Stille Nacht, Rosen Nacht」法被 今井リサ": "lisa法被", 
    "【(15)-(4)】Roselia「Stille Nacht, Rosen Nacht」法被 宇田川あこ": "ako法被", 
    "【(15)-(5)】Roselia「Stille Nacht, Rosen Nacht」法被 白金燐子": "rinko法被"
}
product_fullname = {v: k for k, v in product_mapping.items()}
product_mapping.update(product_fullname)

# 商品对应的专属API字典
product_id = {
    "M码短袖T": "44053408973007",
    "L码长袖T": "44053409104079",
    "XL码短袖T": "44053409169615", 
    "毛巾": "44053412774095", 
    "手环": "44053409366223", 
    "ykn立牌": "44053409431759", 
    "sayo立牌": "44053409497295", 
    "lisa立牌": "44053409595599", 
    "ako立牌": "44053409693903", 
    "rinko立牌": "44053409759439", 
    "吧唧十个装": "44053409824975", 
    "布片挂件": "44053409923279", 
    "文件袋": "44053410021583", 
    "金丝吧唧": "44053410840783",
    "角色吊坠": "44053410971855",
    "连帽衫": "44053411070159",
    "项链": "44053411168463",
    "照片挂画": "44053410087119",
    "ykn小旗": "44053410185423",
    "sayo小旗": "44053410283727",
    "lisa小旗": "44053410349263",
    "ako小旗": "44053410414799", 
    "rinko小旗": "44053410513103",
    "L码长袖T": "44053410676943",
    "XL码长袖T": "44053410775247",
    "ykn法被": "44053411266767", 
    "sayo法被": "44053411528911",
    "lisa法被": "44053411725519",
    "ako法被": "44053411397839",
    "rinko法被": "44053411332303"
}

# 存储商品的库存状态
last_status = {}

# 最大长度限制（64字符）
MAX_LENGTH = 64

# 标记是否是第一次运行
is_first_run = True

# 解析网页获取所有商品的库存信息
def check_stock():
    headers = {'User-Agent': 'Mozilla/5.0'}  # 设置 User-Agent 防止被识别为爬虫
    response = requests.get(URL, headers=headers)
    
    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 获取所有商品的状态
    product_items = soup.find_all('div', class_='product-item')
    
    current_status = {}

    for item in product_items:
        full_name = item.find('a', class_='product-item__title').get_text(strip=True)
        # 使用简称映射
        product_name = product_mapping.get(full_name, full_name)
        
        # 检查商品库存状态
        button = item.find('button', class_='product-item__action-button button button--small button--primary')
        if button:  # 表示有货
            current_status[product_name] = '有货'
        else:
            button_out_of_stock = item.find('button', class_='product-item__action-button button button--small button--disabled')
            if button_out_of_stock:  # 表示无货
                current_status[product_name] = '无货'
            else:
                current_status[product_name] = '未知状态'
    
    return current_status

# 记录状态到txt文件
def record_status_to_file(current_status):
    with open('status.txt', 'w', encoding='utf-8') as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"商品库存状态记录时间: {timestamp}\n")
        for product_name, status in current_status.items():
            file.write(f"{product_name}: {status}\n")
    
    # 自动打开记录的txt文件
    os.startfile('status.txt')

# 发送桌面通知，确保标题和消息不超过最大长度
def send_notification(title, message):
    # 截断超长的标题和消息
    if len(title) > MAX_LENGTH:
        title = title[:MAX_LENGTH]
    if len(message) > MAX_LENGTH:
        message = message[:MAX_LENGTH]
    
    notification.notify(
        title=title,
        message=message,
        timeout=10  # 通知显示的时长（秒）
    )

def add_to_cart(product_name):
    # 获取商品的专属API
    variant_id = product_id.get(product_name)
    if variant_id:
        # 购物车 URL
        cart_url = "https://bushiroad-store.com/cart/add.js"

        # 商品数据
        product_data = {
            "variant_id": variant_id,  # 商品变体 ID
            "quantity": 1,  # 商品数量
        }

        # 请求头，包括 cookie 和其他必要的 headers
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Cookie": cookie,  # 替换为实际的 cookie
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        }

        # 请求体
        data = {
            "items": [{
                "id": product_data["variant_id"],
                "variant_id": product_data["variant_id"],
                "quantity": product_data["quantity"],
            }]
        }

        # 发送 POST 请求
        response = requests.post(cart_url, headers=headers, data=json.dumps(data))

        # 检查响应
        if response.status_code == 200:
            print("商品已成功加入购物车！")
        else:
            print(f"商品加入购物车失败，状态码: {response.status_code}")
            print(response.text)  # 打印返回的错误信息，帮助调试

# 主函数：检查所有商品库存并发送桌面提醒
def monitor_stock():
    global last_status, is_first_run

    while True:
        print("检查商品库存状态...")

        # 获取当前状态
        current_status = check_stock()

        if current_status:
            # 第一次检查：记录商品状态到文件并打开文件，不发送通知
            if is_first_run:  # 只有第一次检查时执行
                record_status_to_file(current_status)
                is_first_run = False  # 更新标记为非第一次运行

            # 比较当前库存状态与之前的状态
            else:
                for product_name, status in current_status.items():
                    if product_name not in last_status or last_status[product_name] != status: 
                        if status == '有货' and last_status.get(product_name) == '无货':
                            # 如果状态从“无货”变为“有货”，加入购物车并打开购物车页面
                            add_to_cart(product_name)
                            webbrowser.open("https://bushiroad-store.com/cart")
                        # 只有库存发生变化时才发送通知
                        send_notification(f"库存变化提醒: {product_name}", f"商品 {product_name} 状态变化为: {status}")
            
            # 更新最后的库存状态
            last_status = current_status
        
        time.sleep(CHECK_INTERVAL)  # 等待

# 启动监控
if __name__ == '__main__':
    monitor_stock()