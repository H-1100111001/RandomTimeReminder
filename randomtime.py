import tkinter as tk
import random as r
import winsound
import time
import threading
import os
import json
import sys

def resource_path(relative_path):#区分开发与非开发环境,用于获取内嵌资源路径
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def config_path(filename):#区分开发与非开发环境,用于获取外部资源路径
    if hasattr(sys, '_MEIPASS'):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, filename)

ingtime_min = 3  # Ingtime的下限（分钟）
ingtime_max = 5  # Ingtime的上限（分钟）
stoptime_min = 8  # stoptime的下限（秒）
stoptime_max = 12  # stoptime的上限（秒）
maxtime = 60  # maxtime，程序最大运行时间（分钟），默认60分钟
newingtime = 0  # 当前的Ingtime值（分钟），随机生成后存储
newstoptime = 0  # 当前的stoptime值（秒），随机生成后存储
exetime = maxtime*60  # 工作流剩余寿命（秒）
filewav_ding = resource_path(r"data/ding.wav")
filewav_dding = resource_path(r"data/dding.wav")
filewav_dingg = resource_path(r"data/dingg.wav")
stopevent = threading.Event()
workthread = None
progress_bar = None
progress_label = None
max_exetime = maxtime * 60  # 初始最大时间（秒）
auto_exit_var = None
#----------------基本函数----------------#
def play_ding_sound():#播放休息提示音ding
    try:
        normalized_path = resource_path(filewav_ding)
        winsound.PlaySound(normalized_path, winsound.SND_ASYNC)
        print('播放ding')
    except Exception as e:print(f'音效错误{e}')

def play_dding_sound():#播放工作提示音dding
    try:
        normalized_path = resource_path(filewav_dding)
        winsound.PlaySound(normalized_path, winsound.SND_ASYNC)
        print('播放dingg')
    except Exception as e:print(f'音效错误{e}')

def play_dingg_sound():#播放结束提示音dingg
    try:
        normalized_path = resource_path(filewav_dingg)
        winsound.PlaySound(normalized_path, winsound.SND_ASYNC)
        print('播放dding')
    except Exception as e:print(f'音效错误{e}')

def setrandomtime():#生成新的ingtime和stoptime
    global newingtime,newstoptime
    newingtime = round(r.uniform(ingtime_min, ingtime_max),2)
    newstoptime = r.randint(stoptime_min, stoptime_max)

def timeloop():#单次计时
    global exetime
    if exetime <= ingtime_min:
        print('剩余时间小于ingtime_min')
        play_dingg_sound()
        stopbutton()
        exetime = 0
        box.after(0, update_progress_bar)
    if exetime <= newingtime*60+newstoptime:
        print('最后一次ingtime')
        play_dding_sound()
        time.sleep(exetime)
        play_dingg_sound()
        exetime = 0
        box.after(0,update_progress_bar)
    else:
        print(f'进入ingtime休眠，此时剩余时间{exetime}')
        play_dding_sound()
        time.sleep(int(newingtime*60));exetime -= int(newingtime * 60)
        box.after(0,update_progress_bar)
        print(f'进入stoptime休眠，此时剩余时间{exetime}')
        play_ding_sound()
        time.sleep(newstoptime);exetime -= newstoptime
        box.after(0,update_progress_bar)

def workfun():#工作流
    try:
        while not stopevent.is_set():
            if exetime <= 0:
                play_dingg_sound()
                stopbutton() # 正常结束时设置标志
                box.after(0, lambda: set_entries_state("normal"))#输入框可编辑
                if auto_exit_var.get():
                    box.after(3000, exitbutton)  # 自动退出
                break
            setrandomtime();print(newingtime, newstoptime);
            timeloop()
    except Exception as e:
        print(f"工作线程错误: {e}")
        box.after(0, lambda: set_entries_state("normal"))
        box.after(0, lambda: set_buttons_state("normal", "disabled"))
#----------------参数配置----------------#
def save_settings():# 保存设置到 JSON 文件
    settings = {"ingtime_min": ingtime_min,
        "ingtime_max": ingtime_max,
        "stoptime_min": stoptime_min,
        "stoptime_max": stoptime_max,
        "maxtime": maxtime}
    try:
        settings_path = config_path('settings.json')
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        print("设置已保存到 settings.json")
    except Exception as e:
        print(f"保存设置失败: {e}")

def load_settings():# 加载设置从 JSON 文件
    global ingtime_min, ingtime_max, stoptime_min, stoptime_max, maxtime
    settings_path = config_path("settings.json")
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        ingtime_min = settings.get("ingtime_min", 3.0)
        ingtime_max = settings.get("ingtime_max", 5.0)
        stoptime_min = settings.get("stoptime_min", 8)
        stoptime_max = settings.get("stoptime_max", 12)
        maxtime = settings.get("maxtime", 60.0)
        exetime = maxtime*60
        max_exetime = exetime
        # 更新输入框
        ingtime_min_entry.delete(0, tk.END)
        ingtime_min_entry.insert(0, str(ingtime_min))
        ingtime_max_entry.delete(0, tk.END)
        ingtime_max_entry.insert(0, str(ingtime_max))
        stoptime_min_entry.delete(0, tk.END)
        stoptime_min_entry.insert(0, str(stoptime_min))
        stoptime_max_entry.delete(0, tk.END)
        stoptime_max_entry.insert(0, str(stoptime_max))
        maxtime_entry.delete(0, tk.END)
        maxtime_entry.insert(0, str(maxtime))
        box.after(0,update_progress_bar)
        print("设置已从 settings.json 加载")
    except FileNotFoundError:
        print("未找到 settings.json，使用默认值")
        print(f"未找到 {settings_path}，生成默认配置文件")
        # 生成默认配置文件
        settings = {"ingtime_min": 3.0,"ingtime_max": 5.0,"stoptime_min": 8,"stoptime_max": 12,"maxtime": 60.0}
    except Exception as e:
        print(f"加载设置失败: {e}")
#----------------窗口----------------#
box = tk.Tk()
box.title('随机计时提示器_V1.0');box.geometry('520x420');
box.config(bg='#f0f0f0'),box.resizable(width=False,height=False)
try:#加载字体
    from tkinter import font as tkfont
    custom_font_path = resource_path('data/SimsunExtG.ttf')
    custom_font = tkfont.Font(family="SimsunExtG.ttf", size=12)
    large_font = tkfont.Font(family="SimsunExtG.ttf", size=20)
    help_font = tkfont.Font(family="SimsunExtG.ttf", size=16)
except Exception as e:
    print(f"无法加载自定义字体: {e}")
    custom_font = ("Arial", 12)  # 回退到默认字体

def helpbutton():#帮助按钮
    helpwin = tk.Toplevel(box)
    x = box.winfo_x()+30
    y = box.winfo_y()+30
    helpwin.geometry(f'480x400+{x}+{y}')
    helpwin.config(bg='#f0f0ff')
    helpwin.resizable(width=False,height=False)
    #边框frame和滚动条
    text_frame = tk.Frame(helpwin, bg='white', bd=2, relief=tk.SUNKEN)
    text_frame.place(x=10, y=10, width=460, height=320)
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    helptextwin = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                       font=help_font, bg='white', padx=10, pady=10)
    helptextwin.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=helptextwin.yview)

    help_text = (
        "随机计时提示器说明：\n"
        "工作时间：以分钟设置随机工作时间的范围\n"
        "休息时间：以秒设置随机停止时间的范围\n"
        "运行时间：以分钟设置学习或工作时间\n"
        "开始：根据输入参数启动计时，输入框锁定\n"
        "停止：中断计时，解锁输入框\n"
        "退出：保存设置并关闭程序\n"
        "----其他：\n"
        "工作时间和最大时间可输入小数\n"
        "休息时间仅可输入整数\n"
        "--参数不正确不会触发计时\n"
        "停止计时不保存计时进度\n"
        "如果遇到什么奇怪BUG，请重启程序"
    )
    helptextwin.insert(tk.END, help_text)
    helptextwin.config(state=tk.DISABLED)
    ok_button = tk.Button(helpwin,
        text="确定",font=large_font,
        command=helpwin.destroy,width=8,
        height=1,bg="#ffffff",relief="raised")
    ok_button.place(x=175, y=340)
    update_parameters()
    print(f'输入值ingtime{ingtime_min*60}~{ingtime_max*60}，stoptime{stoptime_min}~{stoptime_max}，maxtime{maxtime*60}')


def create_sound_test_panel(box):#音效测试框和按钮
    sound_frame = tk.LabelFrame(box, text="试听提示音", font=custom_font,bg='#f0f0f0', padx=5, pady=5)
    sound_frame.place(x=200, y=10, width=220, height=60)
    work_btn = tk.Button(sound_frame, text="工作▷", font=custom_font,command=play_dding_sound, width=6,
                         bg='#e6f7ff', relief=tk.RAISED)
    work_btn.grid(row=0, column=0, padx=5, pady=5)
    rest_btn = tk.Button(sound_frame, text="休息▷", font=custom_font,command=play_ding_sound, width=6,
                         bg='#fff7e6', relief=tk.RAISED)
    rest_btn.grid(row=0, column=1, padx=5, pady=5)
    end_btn = tk.Button(sound_frame, text="终止▷", font=custom_font,command=play_dingg_sound, width=6,
                        bg='#ffebee', relief=tk.RAISED)
    end_btn.grid(row=0, column=2, padx=5, pady=5)

def update_parameters():#更新运行参数
    global ingtime_min, ingtime_max, stoptime_min, stoptime_max, maxtime
    try:
        ingtime_min = float(ingtime_min_entry.get())
        ingtime_max = float(ingtime_max_entry.get())
        stoptime_min = int(stoptime_min_entry.get())
        stoptime_max = int(stoptime_max_entry.get())
        maxtime = float(maxtime_entry.get())
        # 验证输入值合理性
        if ingtime_min < 0 or ingtime_max < ingtime_min:
            print("错误：工作时间最小值需≥0且小于最大值")
            return False
        if stoptime_min < 0 or stoptime_max < stoptime_min:
            print("错误：停止时间最小值需≥0且小于最大值")
            return False
        print(f"更新参数：ingtime_min={ingtime_min}, ingtime_max={ingtime_max}, "
              f"stoptime_min={stoptime_min}, stoptime_max={stoptime_max}")
        save_settings()#保存配置
        return True
    except ValueError:
        print("错误：请输入有效的数字")
        return False

def create_settings_frame(box):# 创建一个带边框的Frame,参数设置分组
    settings_frame = tk.LabelFrame(box, text="计时设置", font=custom_font,bg='#f0f0f0', padx=10, pady=10)
    settings_frame.place(x=50, y=80, width=420, height=180)
    #创建提示文本
    tk.Label(settings_frame, text="工作时间(分)______(min)--______(max)",
             font=custom_font, bg="#f0f0f0").place(x=50, y=20)
    tk.Label(settings_frame, text="休息时间(秒)______(min)--______(max)",
             font=custom_font, bg="#f0f0f0").place(x=50, y=70)
    tk.Label(settings_frame, text="运行时间______分钟",
             font=custom_font, bg="#f0f0f0").place(x=100, y=120)
    #工作时间输入框
    global ingtime_min_entry, ingtime_max_entry
    ingtime_min_entry = tk.Entry(settings_frame, width=5, font=custom_font)
    ingtime_min_entry.insert(0, "3")  # 默认值
    ingtime_min_entry.place(x=150, y=18)
    ingtime_max_entry = tk.Entry(settings_frame, width=5, font=custom_font)
    ingtime_max_entry.insert(0, "5")  # 默认值
    ingtime_max_entry.place(x=255, y=18)
    # 休息时间输入框
    global stoptime_min_entry, stoptime_max_entry
    stoptime_min_entry = tk.Entry(settings_frame, width=5, font=custom_font)
    stoptime_min_entry.insert(0, "8")  # 默认值
    stoptime_min_entry.place(x=150, y=68)
    stoptime_max_entry = tk.Entry(settings_frame, width=5, font=custom_font)
    stoptime_max_entry.insert(0, "12")  # 默认值
    stoptime_max_entry.place(x=255, y=68)
    # 最大运行时间输入框
    global maxtime_entry
    maxtime_entry = tk.Entry(settings_frame, width=5, font=custom_font)
    maxtime_entry.insert(0, "60")  # 默认值
    maxtime_entry.place(x=170, y=118)

def startbutton():#fun开始按钮
    global workthread,exetime,max_exetime
    if workthread and workthread.is_alive():
        stopevent.set()  # 终止旧线程
        try:
            workthread.join(timeout=1.0)
        except Exception as e:
            print(f"线程终止错误: {e}")
    if update_parameters():
        stopevent.clear()
        exetime = maxtime*60
        max_exetime = exetime
        set_entries_state("readonly")#输入框只读
        set_buttons_state(start_state="disabled",stop_state="normal")  # 禁用开始，启用停止
        box.after(0,update_progress_bar)
        workthread = threading.Thread(target=workfun,daemon=True)
        workthread.start()
        print('开始运行')

def stopbutton():#fun停止按钮
    global exetime,workthread
    stopevent.set();exetime = maxtime*60
    try:
        if workthread and workthread.is_alive():
            workthread.join(timeout=1.0)
    except Exception as e:
        print(f"线程终止错误: {e}")
    workthread = None
    stopevent.clear()
    set_entries_state("normal")
    set_buttons_state(start_state="normal",stop_state="disabled")  # 启用开始，禁用停止
    print('停止计时')

def exitbutton():#fun退出按钮
    if update_parameters():
        print('保存并退出')
    box.destroy()

def set_entries_state(state):#统一设置输入框状态
    ingtime_min_entry.configure(state=state)
    ingtime_max_entry.configure(state=state)
    stoptime_min_entry.configure(state=state)
    stoptime_max_entry.configure(state=state)
    maxtime_entry.configure(state=state)

def create_function_button():#功能按钮
    global start_button,stop_button
    help_button = tk.Button(box,text='帮助',font=large_font,command=helpbutton,width=8,height=1,bg='#ffffff',relief='raised')
    help_button.place(x=10,y=10)
    start_button = tk.Button(box,text='开始',font=large_font,command=startbutton,width=8,height=1,bg='#ffffff',relief='raised')
    start_button.place(x=50,y=280)
    stop_button = tk.Button(box,text='停止',font=large_font,command=stopbutton,width=8,height=1,bg='#ffffff',relief='raised')
    stop_button.place(x=190,y=280)
    exit_button = tk.Button(box,text='退出',font=large_font,command=exitbutton,width=8,height=1,bg='#ffffff',relief='raised')
    exit_button.place(x=330,y=280)

def set_buttons_state(start_state,stop_state):#设置按钮是否可交互
    start_button.config(state=start_state)
    stop_button.config(state=stop_state)

def create_progress_bar(box):#创建进度条
    global progress_bar, progress_label
    progress_bar = tk.Canvas(box, width=400, height=20, bg="#ffffff", highlightthickness=1, highlightbackground="#000000")
    progress_bar.place(x=50, y=350)
    progress_bar.create_rectangle(0, 0, 0, 20, fill="#0000ff", outline="")# 初始化填充（0%）
    progress_label = tk.Label(box, text="0%", font=custom_font, bg="#f0f0f0")# 创建百分比标签
    progress_label.place(x=470, y=350)

def update_progress_bar():#更新进度条
    if max_exetime <= 0:
        progress_bar.coords(progress_bar.find_all()[0], 0, 0, 0, 20)
        progress_label.config(text="0%")
        return
    progress = max(0, min(1, exetime/max_exetime))
    width = 400 * (1-progress)
    progress_bar.coords(progress_bar.find_all()[0], 0, 0, width, 20)
    progress_percent = int((1 - progress) * 100)
    progress_label.config(text=f"{progress_percent}%")

def create_auto_exit_checkbox(box):#运行完成后退出复选框
    global auto_exit_var
    auto_exit_var = tk.BooleanVar(value=False)
    tk.Checkbutton(box,text="运行完成后关闭",variable=auto_exit_var,
        font=custom_font,bg="#f0f0f0").place(x=300, y=380)
#----------------运行程序----------------#
create_settings_frame(box)
create_function_button()
load_settings()#加载保存的配置
set_buttons_state(start_state="normal",stop_state="disabled")
create_progress_bar(box)
create_auto_exit_checkbox(box)
create_sound_test_panel(box)
box.mainloop()#让窗口保持运行，放最后一行