import pyautogui as pt
import time
import sys
import pyperclip
import re
import json
import csv
from datetime import datetime
import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from snownlp import SnowNLP
import akshare as ak
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from collections import deque
import os
from pynput.keyboard import Key, Listener


'''作者：李晴函&吕芷琪
   时间：2025.3.26
   当前职位：香港中文大学（深圳）会计学硕士
   作品声明：除非经作者同意，严禁他人用于商业用途；请尊重作者的知识产权！
   '''

# 支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
# 全局字体配置（支持中文显示）
plt.rcParams.update({
    'font.size': 18,                # 基准字号[6](@ref)
    'axes.titlesize': 18,           # 坐标轴标题字号[6](@ref)
    'axes.labelsize': 18,           # 坐标轴标签字号[6](@ref)
    'xtick.labelsize': 15,          # X轴刻度字号
    'ytick.labelsize': 15           # Y轴刻度字号
})


def open_chrome_shortcut():
    #打开chrome快捷方式
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shortcut_name = "Google Chrome.lnk"  # 根据实际文件名修改
    shortcut_path = os.path.normpath(os.path.join(script_dir, shortcut_name))
    if not os.path.exists(shortcut_path):
        raise FileNotFoundError(f"快捷方式不存在: {shortcut_path}")
    os.startfile(shortcut_path)

def get_path(relative_path):
    #获取绝对路径，辅助pyinstaller打包成exe
    try:
        base_path = sys._MEIPASS  # pyinstaller打包后的路径
    except AttributeError:
        base_path = os.path.abspath(".")  # 当前工作目录的路径

    return os.path.normpath(os.path.join(base_path, relative_path))  # 返回实际路径

def fight_against_verification():
    continue_flag = False

    def on_press(key):
        nonlocal continue_flag
        try:
            if key == Key.enter:
                print("\n检测到回车键，程序继续运行...")
                continue_flag = True
                return False  # 停止监听器
        except AttributeError:
            pass

    #自动完成滑动验证
    try:
        image2 = get_path("pictures/2.png")
        location = pt.locateCenterOnScreen(image2, confidence=0.8)
        pt.moveTo(location[0], location[1])
        print("检测到滑块验证码，请手动拖动滑块完成滑块验证。完成验证后请返回浏览器页面，并按回车继续爬取数据。")
        with Listener(on_press=on_press) as listener:
            listener.join()
        while not continue_flag:
            pass
        print("\n检测到回车键，程序继续运行...")
        time.sleep(3)

        # pt.mouseDown()

        #模拟人手动作，对抗反爬机制

        # accelerations = []
        # for _ in range(100):
        #     acc = random.choice([0.8, 1.2, 1.5]) + random.gauss(0, 0.3)
        #     accelerations.append(max(0.5, min(acc, 2.0)))
        #
        # pt.moveTo(location[0] + 800, location[1], duration=1.5, tween=lambda n: n ** accelerations[int(n * 5)])

        # 随机选择一种缓动效果（如先快后慢、弹跳等）
        # tween_functions = [
        #     pt.easeInQuad,  # 先慢后快
        #     pt.easeOutQuad,  # 先快后慢
        #     pt.easeInOutElastic
        # ]
        # random_tween = random.choice(tween_functions)
        #
        # start_x, start_y = location[0], location[1]
        # target_x, target_y = location[0] + 800, location[1]
        # steps = random.randint(2, 3)
        # for i in range(steps):
        #     # 计算分段目标坐标（可加入随机偏移）
        #     start_x = start_x + (target_x - start_x) * 1 / steps + random.randint(-10, 10)
        #     start_y = start_y + (target_y - start_y) * 1 / steps + random.randint(-10, 10)
        #     # 每段随机速度和延时
        #     pt.moveTo(start_x, start_y, duration=random.uniform(0.1, 0.5), tween=random_tween)

        # pt.mouseUp()

    except Exception as e:
        pass

def get_xueqiu_comments(stock_code, n=50): #n表示爬取的页数，每一页爬取20条用户评论
    #直接访问雪球评论数据API借口，复制粘贴JSON数据到本地TXT文件
    start_time = time.time()
    market = 'SZ' if stock_code.startswith(('0', '3')) else 'SH'  # 修正深市判断逻辑
    symbol = f"{market}{stock_code}"
    with open(f"{stock_code}_output.txt", "w", encoding="utf-8") as f:
        open_chrome_shortcut()
        time.sleep(2)
        image1 = get_path("pictures/1.png")
        location = pt.locateCenterOnScreen(image1, confidence=0.8)
        pt.click(location[0], location[1])
        pt.write('https://xueqiu.com/')
        pt.press('enter')
        time.sleep(5)
        for i in range(n-49, n+1):
            print(f'正在爬取股票 {symbol} 的用户评论数据，当前是第{i}页，共50页，百分比进度为 ', "{:.2%}".format(i/50))
            pt.click(location[0], location[1])
            pt.write(f'https://xueqiu.com/query/v1/symbol/search/status?symbol={symbol}&page={i}&count=100')
            pt.press('enter')
            time.sleep(2)
            fight_against_verification()
            pt.moveTo(location[0], location[1]+500)
            pyperclip.copy('')
            pt.click()
            pt.hotkey('ctrl', 'a')
            time.sleep(0.5)
            pt.hotkey('ctrl', 'c')
            clipboard_content = pyperclip.paste()
            f.write(str(clipboard_content)+'\n')
            pt.moveTo(location[0], location[1])
            time.sleep(0.5)
    end_time = time.time()
    print(f'全部主评论数据爬取完毕，共用时{round(end_time-start_time, 2)}秒。')

def get_xueqiu_chlid_comments(stock_code, n): #n表示需要爬取的总页数，每一条评论区的评论数各异
    #直接访问雪球子评论数据API借口，复制粘贴JSON数据到本地TXT文件
    #因雪球网站请求次数限制，仅爬取前50条内容最丰富的评论区数据
    start_time = time.time()
    market = 'SZ' if stock_code.startswith(('0', '3')) else 'SH'  # 修正深市判断逻辑
    symbol = f"{market}{stock_code}"
    with open(f"{stock_code}_child_comments_output.txt", "w", encoding="utf-8") as f:
        open_chrome_shortcut()
        time.sleep(2)
        image1 = get_path("pictures/1.png")
        location = pt.locateCenterOnScreen(image1, confidence=0.8)
        pt.click(location[0], location[1])
        pt.write('https://xueqiu.com/')
        pt.press('enter')
        time.sleep(5)
        for i in range(0, n):
            print(f'正在爬取股票 {symbol} 的评论区数据，当前是第{i+1}页，共{n}页，百分比进度为 ', "{:.2%}".format((i+1)/n))
            pt.click(location[0], location[1])
            pt.write(f'https://xueqiu.com/statuses/v3/comments.json?id={id_list[i]}')
            pt.press('enter')
            time.sleep(2)
            fight_against_verification()
            pt.moveTo(location[0], location[1]+500)
            pyperclip.copy('')
            pt.click()
            pt.hotkey('ctrl', 'a')
            time.sleep(0.5)
            pt.hotkey('ctrl', 'c')
            clipboard_content = pyperclip.paste()
            f.write(str(clipboard_content)+'\n')
            pt.moveTo(location[0], location[1])
            time.sleep(0.5)
    end_time = time.time()
    print(f'全部评论区数据爬取完毕，共用时{round(end_time-start_time, 2)}秒。')

def clean_text(text):
    # 保留中文、汉字及常用中文标点符号
    pattern = r'[^\u4e00-\u9fa5,!?;，。！？；：“”‘’（）《》【】—、\n]'
    return re.sub(pattern, '', text)

def process_comment(comment, stock_code):
    '''

    :param comment: JSON文件中list键下的所有单个字典对象
    :param stock_code:数据所属股票代码
    :return:直接写入输出文件，无返回值
    特别注意：
    'id'是当前评论区别于其他评论的标识符，性质属于主键，具有唯一性，可配合网址https://xueqiu.com/statuses/v3/comments.json?id=XXX
    查找该主评论下的所有评论回复；
    "commentId"是评论特有的id，如果用户发布讨论，其有评论主id，但其commentId为0；但如果用户转发某讨论并作出评论，其既有评论主id，
    也有其commentId，非0；
    "in_reply_to_comment_id"是用户评论了转发的评论，"in_reply_to_comment_id"的值等于上述转发的评论的"commentId"的值；
    "root_in_reply_to_status_id"是用户评论了转发的评论，"root_in_reply_to_status_id"的值等于上述原始主讨论的"Id"的值；
    因此为实现尽可能获取更多评论内容，我们先爬取主评论API网址，具体网址为：https://xueqiu.com/query/v1/symbol/search/status?symbol=SZ002570&page=1&count=100
    再利用reply_count不为0的评论的主id，爬取评论区内容，具体网址为：https://xueqiu.com/statuses/v3/comments.json?id=XXX
    主评论储存在list键下的列表中，子评论储存在comments键下的列表中，单个评论均为字典结构

    '''

    # 提取评论主id
    comment_id = comment.get('id', '')

    # 提取评论的隶属主评论id，由于当前函数处理的都是主评论，因此隶属主评论id等于评论主id
    source_comment_id = comment.get('id', '')

    # 提取评论的用户id
    user_id = comment.get('user_id', '')

    # 提取评论日期
    created_at = comment.get('created_at')
    if created_at:
        # 转换时间戳，假设是毫秒
        dt = datetime.fromtimestamp(created_at / 1000)
        date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        date_str = ''

    # 提取评论内容
    text = comment.get('text', '')
    description = comment.get('description', '')
    comment_text = clean_text(text) if text else description

    # 提取回复数量
    reply_count = comment.get('reply_count', 0)

    # 提取转发数量
    retweet_count = comment.get('retweet_count', 0)

    # 提取点赞数量
    like_count = comment.get('like_count', 0)

    # 提取收藏数量
    fav_count = comment.get('fav_count', 0)

    # 提取浏览数量
    view_count = comment.get('view_count', 0)

    # 提取来源
    source = comment.get('source', '')


    # 写入CSV
    writer.writerow([stock_code, comment_id, source_comment_id, user_id, date_str, comment_text, reply_count, retweet_count, like_count,
                     fav_count, view_count, source])

def process_child_comment(comment, stock_code):
    '''

    :param comment: JSON文件中list键下的所有单个字典对象
    :param stock_code:数据所属股票代码
    :return:直接写入输出文件，无返回值
    特别注意：
    'id'是当前评论区别于其他评论的标识符，性质属于主键，具有唯一性，可配合网址https://xueqiu.com/statuses/v3/comments.json?id=XXX
    查找该主评论下的所有评论回复；
    "commentId"是评论特有的id，如果用户发布讨论，其有评论主id，但其commentId为0；但如果用户转发某讨论并作出评论，其既有评论主id，
    也有其commentId，非0；
    "in_reply_to_comment_id"是用户评论了转发的评论，"in_reply_to_comment_id"的值等于上述转发的评论的"commentId"的值；
    "root_in_reply_to_status_id"是用户评论了转发的评论，"root_in_reply_to_status_id"的值等于上述原始主讨论的"Id"的值；
    因此为实现尽可能获取更多评论内容，我们先爬取主评论API网址，具体网址为：https://xueqiu.com/query/v1/symbol/search/status?symbol=SZ002570&page=1&count=100
    再利用reply_count不为0的评论的主id，爬取评论区内容，具体网址为：https://xueqiu.com/statuses/v3/comments.json?id=XXX
    主评论储存在list键下的列表中，子评论储存在comments键下的列表中，单个评论均为字典结构

    '''

    # 提取评论主id
    comment_id = comment.get('id', '')

    # 提取评论的隶属主评论id，由于当前函数处理的都是子评论，因此隶属主评论id等于"root_in_reply_to_status_id"
    source_comment_id = comment.get('root_in_reply_to_status_id', '')

    # 提取评论的用户id
    user_id = comment.get('user_id', '')

    # 提取评论日期
    created_at = comment.get('created_at')
    if created_at:
        # 转换时间戳，假设是毫秒
        dt = datetime.fromtimestamp(created_at / 1000)
        date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        date_str = ''

    # 提取评论内容
    text = comment.get('text', '')
    description = comment.get('description', '')
    comment_text = clean_text(text) if text else description

    # 提取回复数量
    reply_count = comment.get('reply_count', 0)

    # 提取转发数量
    retweet_count = comment.get('retweet_count', 0)

    # 提取点赞数量
    like_count = comment.get('like_count', 0)

    # 提取收藏数量
    fav_count = comment.get('fav_count', 0)

    # 提取浏览数量
    view_count = comment.get('view_count', 0)

    # 提取来源
    source = comment.get('source', '')


    # 写入CSV
    writer.writerow([stock_code, comment_id, source_comment_id, user_id, date_str, comment_text, reply_count, retweet_count, like_count,
                     fav_count, view_count, source])

    # 处理评论的子评论，回溯算法
    cur_child_comments = comment.get('child_comments', [])
    for cur_child_comment in cur_child_comments:
        process_child_comment(cur_child_comment, stock_code)

def plot_wordcloud():
    # new_stopwords = ['曰', '吾', '皆', '见', '遂', '欲', '便', '汝', '操', '问', '二人', '走', '令', '说', '不可', '不能',
    #                 '出', '请', '张', '时', '回', '二', '引', '更', '正', '前', '不敢', '忽']
    # with open('cn_stopwords.txt', "a", encoding="utf-8") as f:
    #     f.write("\n" + "\n".join(new_stopwords))

    df = pd.read_csv(f'{stock_code}_output.csv', encoding='utf-8-sig')
    text = ''.join([str(text) for text in df['评论内容']])
    word_list = jieba.lcut(text, cut_all=False)
    stopwords = open('cn_stopwords.txt', 'r', encoding='utf-8').read()
    stopwords = stopwords.split('\n')
    word_list_sw = [w for w in word_list if w not in stopwords]
    frequency_table = Counter(word_list_sw)

    wc = WordCloud(
        font_path='SourceHanSerifK-Light.otf',
        width=1600,
        height=800,
        scale=4,
        max_words=100,
        max_font_size=200,
        min_font_size=10,
        colormap='cool',
        background_color='white',
        repeat=False
    )
    wc.generate_from_frequencies(frequency_table)
    plt.imshow(wc)
    plt.axis("off")
    plt.savefig(f'{symbol}词云图.png', dpi=300)
    plt.close()

def plot_sentiment_timeseries():

    def contextual_score(comment):
        context_window.append(comment)
        recent_text = " ".join(context_window)
        # 综合近期语境
        return round((SnowNLP(recent_text).sentiments * 0.4 + SnowNLP(comment).sentiments * 0.6) * 100, 0)

    # 准备股票领域语料库
    # sentiment.train(
    #     '负面词典.txt',  # 负面评论：如"财报暴雷""减持利空"
    #     '正面词典.txt'  # 正面评论：如"主力增持""业绩超预期"
    # )
    # sentiment.save('stock_sentiment.marshal')
    # 替换默认模型（网页1）

    df = pd.read_csv(f'{stock_code}_output.csv', encoding='utf-8-sig')
    df['评论内容'] = df['评论内容'].astype(str)
    df['情绪指数'] = df['评论内容'].apply(contextual_score)
    # 转换日期格式并提取年月日，去掉小时和分钟
    df['评论日'] = pd.to_datetime(df['评论日期']).dt.date
    # 按评论日分组计算情绪得分平均值
    daily_avg = df.groupby('评论日', as_index=False)['情绪指数'].mean()

    # 获取股票历史行情
    stock_df = ak.stock_zh_a_hist(symbol=f'{stock_code}', adjust="hfq")
    stock_df['日期'] = pd.to_datetime(stock_df['日期']).dt.date
    close_prices = stock_df[['日期', '收盘']].rename(columns={'日期': '评论日', '收盘': '收盘价'})
    # 按评论日左连接合并
    daily_avg_and_close_prices = pd.merge(
        left=daily_avg,
        right=close_prices,
        on='评论日',
        how='left'
    )

    # 绘制双坐标轴图表
    plt.figure(figsize=(12, 6))
    plt.title(f'{symbol}近期情绪指数与收盘价时间序列', fontsize=14)

    # 主坐标轴（情绪指数）
    ax1 = plt.gca()
    color = 'tab:red'
    ax1.set_xlabel('评论日期')
    ax1.set_ylabel('情绪指数', color=color)
    ax1.plot(daily_avg_and_close_prices['评论日'],
             daily_avg_and_close_prices['情绪指数'],
             color=color,
             marker='o',
             linewidth=2,
             markersize=8)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)

    # 次坐标轴（收盘价）
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('收盘价（元）', color=color)
    ax2.plot(daily_avg_and_close_prices['评论日'],
             daily_avg_and_close_prices['收盘价'],
             color=color,
             linestyle='--',
             marker='^',
             linewidth=2,
             markersize=8)
    ax2.tick_params(axis='y', labelcolor=color)

    # 优化显示
    plt.xticks(rotation=45)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    # 添加图例
    ax1.legend(['情绪指数'], loc='upper left')
    ax2.legend(['收盘价'], loc='upper right')

    plt.savefig(f'{symbol}近期情绪指数与收盘价时间序列图.png', dpi=300)
    plt.close()

def PDF_creation():
    try:
        c = canvas.Canvas(f'{symbol}股票近期情绪分析报告.pdf', pagesize=A4)
        width, height = A4

        # 标题
        c.setFont("SimSun", 16)
        c.drawString(200, height - 50, f'{symbol}股票近期情绪分析报告')

        img1_path = f'{symbol}近期情绪指数与收盘价时间序列图.png'
        img2_path = f'{symbol}词云图.png'

        # 第一张图片（动态计算高度）
        img1_y = height - 1100
        img1_width, img1_height = c.drawImage(img1_path, 50, img1_y, width=500, preserveAspectRatio=True)
        c.setFont("SimSun", 12)
        c.drawString(50, img1_y + 750, '近期情绪指数与收盘价时间序列图通过双轴折线图形式展示了本交易周期内雪球网股票评论\n')
        c.drawString(50, img1_y + 730, '情绪指数（左轴）与收盘价（右轴）的动态联动关系。市场预期很可能对价格走势起到先行')
        c.drawString(50, img1_y + 710,
                     '指引作用。投资有风险，入市需谨慎。')

        # 第二张图片（新页或下方）
        img2_y = img1_y - img1_height + 1600  # 留出50点间距
        c.drawImage(img2_path, 50, img2_y, width=500, preserveAspectRatio=True)
        c.drawString(50, img2_y + 580, "高频汉语词汇词云图通过字体大小反映该词汇在本交易周期内雪球网股票评论中出现的次数，")
        c.drawString(50, img2_y + 560, "越大的字体出现的次数越多。报告使用者可通过高频关键词快速获取与该股票相关的热点话题。")

        c.save()
        print("PDF生成成功！")
    except Exception as e:
        print(f"错误发生: {str(e)}")



if __name__ == '__main__':
    stock_code = input("请输入股票代码（如000001）:").strip()
    n = input("请输入想要抓取页数的数量n（n为50的正整数倍数，一般为n=50，或n=100表示下载第51至100页评论）:").strip()
    market = 'SZ' if stock_code.startswith(('0', '3')) else 'SH'  # 修正深市判断逻辑
    symbol = f"{market}{stock_code}"
    get_xueqiu_comments(stock_code, int(n))    #将雪球网主评论数据抓取到本地，n为爬取的主评论页数，请输入50的倍数，如n=100即下载第51至100页评论

    with open(f'{stock_code}_output.txt', 'r') as f:    #读取本地抓取的数据
        comments = f.read().strip().split('\n')

    with open(f'{stock_code}_output.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ['股票代码', '评论id', '隶属主评论id', '评论用户id', '评论日期', '评论内容', '回复量', '转发量', '点赞量', '收藏量',
             '浏览量', '来源'])
        # 遍历主评论列表
        for page in comments:
            page = json.loads(page)
            for comment in page['list']:
                process_comment(comment, symbol)    #将每一条主评论数据写入CSV文件

    # 评论区爬取代码，受限于雪球网请求次数限制，我们不爬取完整的评论区代码，仅爬取筛选出的TOP50评论区
    df = pd.read_csv(f'{stock_code}_output.csv', encoding='utf-8-sig')
    df.sort_values(by='回复量', inplace=True, ascending=False)
    filtered_df = df.iloc[:50, :]
    id_list = filtered_df['评论id'].astype(str).tolist()  #读取主评论文件，筛选出有评论区的评论id

    get_xueqiu_chlid_comments(stock_code, n=len(id_list))   #将雪球网子评论数据抓取到本地

    with open(f'{stock_code}_child_comments_output.txt', 'r') as f:    #读取本地抓取的数据
        child_comments = f.read().strip().split('\n')

    with open(f'{stock_code}_output.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        # 遍历评论区列表
        for page in child_comments:
            page = json.loads(page)
            for child_comment in page['comments']:
                process_child_comment(child_comment, symbol)    #将每一条子评论与子评论的回复数据写入CSV文件

    context_window = deque(maxlen=3)  # 滑动窗口
    plot_wordcloud()    #绘制词云图
    plot_sentiment_timeseries()    #绘制情感指数与股价时间序列
    PDF_creation()    #将2份图表汇入PDF文件










