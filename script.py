import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import json
import re
import concurrent.futures
import webbrowser
import time
from datetime import datetime

class StockChecker:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Bushiroad Online Shop")
        self.window.geometry("1200x900")
        
        # 设置主题颜色
        self.bg_color = "#f8f9fa"
        self.accent_color = "#3498db"
        self.text_color = "#2c3e50"
        self.button_hover = "#2980b9"
        self.window.configure(bg=self.bg_color)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("Treeview", 
                           background=self.bg_color,
                           foreground=self.text_color,
                           rowheight=35,  # 增加行高
                           fieldbackground=self.bg_color,
                           font=('微软雅黑', 11))
        self.style.configure("Treeview.Heading", 
                           font=('微软雅黑', 12, 'bold'),
                           background=self.bg_color,  # 改为背景色
                           foreground=self.text_color,  # 改为文字颜色
                           padding=5)
        self.style.map('Treeview.Heading',
                      background=[('active', self.bg_color)],
                      foreground=[('active', self.accent_color)])  # 悬停时改变文字颜色
        
        # 创建主框架
        main_frame = tk.Frame(self.window, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # 创建标题
        title_label = tk.Label(main_frame, 
                             text="商品库存查询系统",
                             font=('微软雅黑', 24, 'bold'),
                             bg=self.bg_color,
                             fg=self.accent_color)
        title_label.pack(pady=(0, 30))
        
        # 创建商品展示区域
        tree_frame = tk.Frame(main_frame, bg=self.bg_color)
        tree_frame.pack(fill='both', expand=True)
        
        self.tree = ttk.Treeview(tree_frame, 
                                columns=('商品名称', '库存数量', '价格', '商品ID'),
                                show='headings',
                                selectmode='browse',
                                height=8)
        self.tree.heading('商品名称', text='商品名称')
        self.tree.heading('库存数量', text='库存数量')
        self.tree.heading('价格', text='价格')
        self.tree.heading('商品ID', text='商品ID')
        self.tree.column('商品名称', width=600)  # 增加商品名称列宽
        self.tree.column('库存数量', width=80)   # 减小库存数量列宽
        self.tree.column('价格', width=80)       # 减小价格列宽
        self.tree.column('商品ID', width=0, stretch=False)
        self.tree.pack(side='left', fill='both', expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 创建控制区域
        control_frame = tk.Frame(main_frame, bg=self.bg_color)
        control_frame.pack(fill='x', pady=30)
        
        # 数量设置区域
        quantity_frame = tk.Frame(control_frame, bg=self.bg_color)
        quantity_frame.pack(side='left', padx=20)
        
        tk.Label(quantity_frame, 
                text="数量:",
                bg=self.bg_color,
                font=('微软雅黑', 12)).pack(side='left', padx=10)
        
        self.quantity_var = tk.StringVar(value="1")
        quantity_entry = tk.Entry(quantity_frame,
                                textvariable=self.quantity_var,
                                width=6,
                                font=('微软雅黑', 12),
                                justify='center',
                                relief='solid',
                                bd=1)
        quantity_entry.pack(side='left', padx=10)
        
        def adjust_quantity(delta):
            try:
                current = int(self.quantity_var.get())
                new_value = max(1, current + delta)
                self.quantity_var.set(str(new_value))
            except ValueError:
                self.quantity_var.set("1")
        
        def create_quantity_button(text, command):
            btn = tk.Button(quantity_frame,
                          text=text,
                          command=command,
                          width=4,
                          font=('微软雅黑', 12),
                          bg=self.accent_color,
                          fg='white',
                          relief='flat',
                          cursor='hand2')
            def on_enter(e):
                btn['background'] = self.button_hover
            def on_leave(e):
                btn['background'] = self.accent_color
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            btn.pack(side='left', padx=5)
            return btn
        minus_btn = create_quantity_button("-", lambda: adjust_quantity(-1))
        plus_btn = create_quantity_button("+", lambda: adjust_quantity(1))
        
        # 总价和特典数量（放到同一行，靠右，防止被按钮挤压）
        info_inline_frame = tk.Frame(control_frame, bg=self.bg_color)
        info_inline_frame.pack(side='right', padx=20, fill='x', expand=True)
        self.total_price_label = tk.Label(info_inline_frame,
                                        text="总价: 0円",
                                        font=('微软雅黑', 14, 'bold'),
                                        bg=self.bg_color,
                                        fg=self.accent_color,
                                        anchor='e')
        self.total_price_label.pack(side='right', padx=20)
        self.bonus_label = tk.Label(info_inline_frame,
                                  text="特典数量: 0个",
                                  font=('微软雅黑', 14, 'bold'),
                                  bg=self.bg_color,
                                  fg=self.accent_color,
                                  anchor='e')
        self.bonus_label.pack(side='right', padx=20)
        
        # 按钮区域
        button_frame = tk.Frame(control_frame, bg=self.bg_color)
        button_frame.pack(side='left', padx=30)
        def create_button(parent, text, command):
            # 根据按钮内容调整宽度
            if text == "刷新库存":
                btn = tk.Button(parent,
                              text=text,
                              command=command,
                              font=('微软雅黑', 12),
                              bg=self.accent_color,
                              fg='white',
                              padx=8,
                              pady=8,
                              relief='flat',
                              cursor='hand2',
                              width=8)
            elif text == "批量提交":
                btn = tk.Button(parent,
                              text=text,
                              command=command,
                              font=('微软雅黑', 12),
                              bg=self.accent_color,
                              fg='white',
                              padx=30,
                              pady=8,
                              relief='flat',
                              cursor='hand2',
                              width=18)
            else:
                btn = tk.Button(parent,
                              text=text,
                              command=command,
                              font=('微软雅黑', 12),
                              bg=self.accent_color,
                              fg='white',
                              padx=20,
                              pady=8,
                              relief='flat',
                              cursor='hand2')
            def on_enter(e):
                btn['background'] = self.button_hover
            def on_leave(e):
                btn['background'] = self.accent_color
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            return btn
        add_to_cart_btn = create_button(button_frame, "加入购物车清单", self.add_to_cart_list)
        add_to_cart_btn.pack(side='left', padx=10)
        refresh_btn = create_button(button_frame, "刷新库存", self.refresh_stock)
        refresh_btn.pack(side='left', padx=10)
        submit_btn = create_button(button_frame, "批量提交", self.submit_cart_list)
        submit_btn.pack(side='left', padx=10)
        
        # 购物车清单区域（加滚动条）
        cart_frame = tk.LabelFrame(main_frame, 
                                 text="购物车清单",
                                 bg="#eaf2fb",
                                 font=('微软雅黑', 14, 'bold'),
                                 fg=self.accent_color,
                                 bd=3,
                                 relief='groove')
        cart_frame.pack(fill='x', pady=20, ipady=10)
        cart_tree_frame = tk.Frame(cart_frame, bg="#eaf2fb")
        cart_tree_frame.pack(fill='both', expand=True)
        self.cart_tree = ttk.Treeview(cart_tree_frame,
                                    columns=('商品名称', '数量', '单价', '小计', '商品ID'),
                                    show='headings',
                                    height=12)
        self.cart_tree.heading('商品名称', text='商品名称')
        self.cart_tree.heading('数量', text='数量')
        self.cart_tree.heading('单价', text='单价')
        self.cart_tree.heading('小计', text='小计')
        self.cart_tree.heading('商品ID', text='商品ID')
        self.cart_tree.column('商品名称', width=700)
        self.cart_tree.column('数量', width=100)
        self.cart_tree.column('单价', width=100)
        self.cart_tree.column('小计', width=100)
        self.cart_tree.column('商品ID', width=0, stretch=False)
        # 滚动条
        cart_vsb = ttk.Scrollbar(cart_tree_frame, orient='vertical', command=self.cart_tree.yview)
        cart_hsb = ttk.Scrollbar(cart_tree_frame, orient='horizontal', command=self.cart_tree.xview)
        self.cart_tree.configure(yscrollcommand=cart_vsb.set, xscrollcommand=cart_hsb.set)
        cart_vsb.pack(side='right', fill='y')
        cart_hsb.pack(side='bottom', fill='x')
        self.cart_tree.pack(fill='both', expand=True, padx=30, pady=15)
        self.cart_tree.tag_configure('bigfont', font=('微软雅黑', 13))
        
        # 信息显示区域
        info_frame = tk.Frame(main_frame, bg=self.bg_color)
        info_frame.pack(fill='x', pady=20)
        
        self.time_label = tk.Label(info_frame,
                                 text="",
                                 font=('微软雅黑', 12),
                                 bg=self.bg_color,
                                 fg=self.text_color)
        self.time_label.pack(side='right', padx=20)
        
        # 特典说明区域
        bonus_frame = tk.LabelFrame(main_frame, 
                                  text="特典说明",
                                  bg=self.bg_color,
                                  font=('微软雅黑', 12))
        bonus_frame.pack(fill='x', pady=20)
        
        bonus_info = """特典规则：
※1会計3枚までのお渡しとなります。
※5,000円ごとに3種類の中からランダムで1点のお渡しです。
※20,000円以上ご購入いただいても3枚のお渡しとなります。
※お渡しはランダムとなります。15,000円以上ご購入いただいてもコンプリートは保証されません。"""
        
        tk.Label(bonus_frame,
                text=bonus_info,
                justify='left',
                font=('微软雅黑', 12),
                bg=self.bg_color,
                fg=self.text_color).pack(padx=20, pady=10)
        
        # 绑定事件
        self.tree.bind('<ButtonRelease-1>', self.on_select)
        
        # 初始化
        self.product_id_mapping = {}
        self.cart_list = []
        self.cookie = None
        
        # 启动时间更新
        self.update_time()
        
        # 初始化加载
        self.refresh_stock()
        self.get_cookie()

    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.time_label.config(text=f"当前时间: {current_time}")
        self.window.after(1, self.update_time)  # 每毫秒更新一次

    def calculate_bonus(self, total_price):
        """计算特典数量"""
        # 每5000円获得1个特典，最多3个
        bonus = min(3, total_price // 5000)
        return bonus

    def get_cookie(self):
        """获取用户输入的Cookie"""
        cookie_window = tk.Toplevel(self.window)
        cookie_window.title("输入Cookie")
        cookie_window.geometry("400x150")
        
        tk.Label(cookie_window, text="请输入购物车的Cookie：").pack(pady=10)
        cookie_entry = tk.Entry(cookie_window, width=50)
        cookie_entry.pack(pady=10)
        
        def save_cookie():
            self.cookie = cookie_entry.get()
            cookie_window.destroy()
        
        tk.Button(cookie_window, text="确定", command=save_cookie).pack(pady=10)
        cookie_window.transient(self.window)
        cookie_window.grab_set()
        self.window.wait_window(cookie_window)
    
    def add_to_cart_list(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择商品！")
            return
        item = self.tree.item(selected_item[0])
        product_name = item['values'][0]
        variant_id = self.product_id_mapping.get(product_name)
        price = float(item['values'][2])  # 直接使用商品列表中的价格
        if not variant_id:
            messagebox.showerror("错误", "未找到商品ID！")
            return
        try:
            quantity = int(self.quantity_var.get())
            if quantity < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数量！")
            return
        # 检查购物车清单中是否已存在该商品，存在则累加数量
        for entry in self.cart_list:
            if entry['variant_id'] == variant_id:
                entry['quantity'] += quantity
                break
        else:
            self.cart_list.append({
                'name': product_name,
                'variant_id': variant_id,
                'quantity': quantity,
                'price': price
            })
        self.refresh_cart_tree()

    def refresh_cart_tree(self):
        # 刷新购物车清单展示区
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        total_price = 0
        for entry in self.cart_list:
            subtotal = entry['price'] * entry['quantity']
            total_price += subtotal
            self.cart_tree.insert('', 'end', values=(
                entry['name'],
                entry['quantity'],
                f"{int(entry['price'])}円",  # 显示整数价格
                f"{int(subtotal)}円",  # 显示整数小计
                entry['variant_id']
            ))
        # 更新总价和特典数量
        self.total_price_label.config(text=f"总价: {int(total_price)}円")  # 显示整数总价
        bonus = self.calculate_bonus(total_price)
        self.bonus_label.config(text=f"特典数量: {int(bonus)}个")

    def submit_cart_list(self):
        if not self.cart_list:
            messagebox.showwarning("警告", "购物车清单为空！")
            return
        if not self.cookie:
            messagebox.showwarning("警告", "请先设置Cookie！")
            self.get_cookie()
            return
        # 组装items
        items = []
        for entry in self.cart_list:
            items.append({
                "id": entry['variant_id'],
                "variant_id": entry['variant_id'],
                "quantity": entry['quantity']
            })
        # 清理Cookie
        cookie = self.cookie.strip().replace('\\n', '').replace('\\r', '').replace('\n', '').replace('\r', '')
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        data = {"items": items}
        try:
            response = requests.post("https://bushiroad-store.com/cart/add.js", headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                messagebox.showinfo("成功", "所有商品已成功加入购物车！")
                webbrowser.open("https://bushiroad-store.com/cart")
                self.cart_list.clear()
                self.refresh_cart_tree()
            else:
                messagebox.showerror("错误", f"加入购物车失败，状态码: {response.status_code}")
        except Exception as e:
            messagebox.showerror("错误", f"加入购物车时发生错误: {str(e)}")

    def refresh_stock(self):
        """刷新库存信息（多线程+价格处理+名称翻译）"""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            url = "https://bushiroad-store.com/pages/ppp_live2025"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            products = soup.find_all('a', class_='product-item__title')
            product_links = [p['href'] if p['href'].startswith('http') else 'https://bushiroad-store.com' + p['href'] for p in products]

            results = []

            def fetch_detail(link):
                try:
                    detail_resp = requests.get(link, timeout=10)
                    detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                    script_tag = detail_soup.find('script', type='application/json', attrs={'data-product-json': True})
                    if script_tag:
                        data = json.loads(script_tag.string)
                        product = data.get('product', {})
                        name = product.get('title', '未知商品')
                        price = "未知"
                        variant_id = None
                        
                        if 'variants' in product and product['variants']:
                            variant = product['variants'][0]
                            variant_id = str(variant.get('id', ''))
                            price_raw = str(variant.get('price', '未知'))
                            # 去掉尾部两个0
                            price_num = re.sub(r'[^\d]', '', price_raw)
                            if price_num.isdigit() and len(price_num) > 2:
                                price = str(float(price_num[:-2]) / 10 * 11)  # 880 -> 8.8 -> 96.8
                            else:
                                price = price_raw
                        
                        inventories = data.get('inventories', {})
                        inventory_quantity = "未知"
                        if inventories:
                            for inv in inventories.values():
                                inventory_quantity = inv.get('inventory_quantity', '未知')
                                break
                        
                        return (name, inventory_quantity, price, variant_id)
                    else:
                        return ("未找到JSON", "未知", "未知", None)
                except Exception as e:
                    print(f"解析商品详情时发生错误: {str(e)}")
                    return ("解析失败", "未知", "未知", None)

            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                for result in executor.map(fetch_detail, product_links):
                    results.append(result)

            # 更新商品ID映射
            for name, inventory_quantity, price, variant_id in results:
                if variant_id:
                    self.product_id_mapping[name] = variant_id
                self.tree.insert('', 'end', values=(name, inventory_quantity, price, variant_id))

        except Exception as e:
            print(f"刷新库存时发生错误: {str(e)}")
    
    def on_select(self, event):
        # 选中商品时，自动将数量输入框重置为1
        selected_item = self.tree.selection()
        if selected_item:
            self.quantity_var.set("1")
    
    def run(self):
        """运行程序"""
        self.window.mainloop()

if __name__ == "__main__":
    app = StockChecker()
    app.run()

    def parse_html(self):
        """解析HTML文件获取商品信息"""
        try:
            # 读取本地HTML文件
            with open('bushiroad-store.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # 查找所有商品项
            products = soup.find_all('div', class_='product-item')
            
            for product in products:
                # 获取商品名称
                name_elem = product.find('h3', class_='product-name')
                name = name_elem.text.strip() if name_elem else "未知商品"
                
                # 获取库存状态
                stock_elem = product.find('div', class_='stock-status')
                stock = stock_elem.text.strip() if stock_elem else "未知"
                
                # 获取价格
                price_elem = product.find('span', class_='price')
                price = price_elem.text.strip() if price_elem else "未知"
                
                # 将数据插入到树形视图
                self.tree.insert('', 'end', values=(name, stock, price))
                
        except FileNotFoundError:
            print("未找到HTML文件")
        except Exception as e:
            print(f"解析HTML时发生错误: {str(e)}")
