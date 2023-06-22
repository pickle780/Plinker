#-*-coding:utf-8-*-
#程序员：pickle780（本文档编写者）
#版本：V1.2
#日期：2023.06.22
import serial
from serial.tools import list_ports
import tkinter as tk
from tkinter.messagebox import *
from tkinter import ttk
import sys
import threading
#程序的目的是开发一个gui界面，用于发送指令
# gui界面的内容包括：
# 1.串口号 
# 2.波特率 
# 3.发送按钮 
# 4.发送内容 
# 5.定时发送功能勾选@TODO/半成品
# 6.定时发送时间间隔 
# 7.图像显示区域@TODO
class serial_contact:
    class ToolTip:
        def __init__(self, widget, text):
            self.widget = widget
            self.text = text
            self.tooltip = None
            self.entered = False
            self.widget.bind("<Enter>", self.enter)
            self.widget.bind("<Leave>", self.leave)

        def enter(self, event):
            self.entered = True
            self.widget.after(3000, self.show_tooltip)

        def leave(self, event):
            self.entered = False
            self.hide_tooltip()

        def show_tooltip(self):
            if self.entered:
                x, y, _, _ = self.widget.bbox("insert")
                x += self.widget.winfo_rootx() + 25
                y += self.widget.winfo_rooty() + 25

                self.tooltip = tk.Toplevel(self.widget)
                self.tooltip.wm_overrideredirect(True)
                self.tooltip.wm_geometry(f"+{x}+{y}")

                label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
                label.pack()

        def hide_tooltip(self):
            if self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None

    def __init__(self):
        self.main_window = tk.Tk()
        self.data_init()
        #基本参数初始化
        self.layout_init()
        #界面布局初始化
        self.bind_event_main()
        #绑定事件
        self.main_layout_tips_init()
        #提示信息初始化
        self.main_window.mainloop()
        #界面主循环

    def main_layout_tips_init(self):
        self.tooltip_connect = self.ToolTip(self.button_connect, "连接到串口")
        self.tooltip_send = self.ToolTip(self.button_send, "发送数据")
        self.tooltip_clear = self.ToolTip(self.button_clear, "清空发送内容")
        self.tooltip_disconnect = self.ToolTip(self.button_disconnect, "断开串口连接")
        self.tooltip_more = self.ToolTip(self.button_more, "更多选项")
        self.tooltip_send_content = self.ToolTip(self.send_content, "按ctrl+enter发送内容")
        self.tooltip_clear_recive = self.ToolTip(self.button_clear_recive, "清空接收内容")

    def bind_event_main(self):
        self.main_window.bind("<Control-Return>",self.ctrl_enter_send)
        #绑定ctrl+enter发送        

    def ctrl_enter_send(self,event):
        if event.keysym == "Return" and event.state == 12:
            #Ctrl+Enter发送,删除一个enter
            self.send_content.delete("end-2c")
            self.send_content.config(state=tk.DISABLED)
            self.send() 
            self.send_content.config(state=tk.NORMAL)
    
    def data_init(self):
        #基本参数初始化
        self.time_send_circle_ms = 1000
        #定时发送时间间隔
    def layout_init(self):
        #界面布局初始化
        self.main_window.iconbitmap("icon.ico")
        self.main_window.title("plinker")
        self.main_window.resizable(0, 0)
        #可自由拖动窗口大小

        self.main_window.geometry("+{}+{}".format(int((self.main_window.winfo_screenwidth() - self.main_window.winfo_reqwidth()) / 2), int((self.main_window.winfo_screenheight() - self.main_window.winfo_reqheight()) / 2)))
        #窗口居中

        self.main_window.protocol("WM_DELETE_WINDOW", lambda:self.askclose(self.main_window,))

        self.serial_port = tk.StringVar()
        self.serial_port.set("请选择串口")

        self.baund_rate = tk.StringVar()
        self.baund_rate.set("请选择波特率")
        # 顶部区域布局
        self.top_frame = tk.Frame(self.main_window)
        self.top_frame.pack(side=tk.TOP, padx=10, pady=10)

        self.optionMenu_serial_port = ttk.Combobox(self.top_frame, textvariable=self.serial_port, values=list_ports.comports())
        self.optionMenu_serial_port.pack(side=tk.LEFT)

        self.optionMenu_baund_rate = ttk.Combobox(self.top_frame, textvariable=self.baund_rate, values=["9600", "115200"])
        self.optionMenu_baund_rate.pack(side=tk.LEFT, padx=(10, 0))

        # 接收内容区域布局
        self.receive_frame = tk.Frame(self.main_window)
        self.receive_frame.pack(anchor=tk.NW, padx=10, pady=(0, 10))

        self.recive_content = tk.Text(self.receive_frame, height=5, width=30)
        self.recive_content.config(state=tk.DISABLED)
        self.recive_content.pack(side=tk.LEFT)

        self.receive_scrollbar = tk.Scrollbar(self.receive_frame, orient=tk.VERTICAL, command=self.recive_content.yview)
        self.receive_scrollbar.pack(side=tk.LEFT, fill=tk.Y)


        self.button_clear_recive = tk.Button(self.receive_frame, text="清空\n接收", command=self.clear_recive)
        self.button_clear_recive.pack(side=tk.LEFT,fill="y")
        self.button_connect = tk.Button(self.receive_frame, text="连接", command=self.connect)
        self.button_connect.pack(side=tk.LEFT,fill="y")
        self.button_send = tk.Button(self.receive_frame, text="发送", command=self.send)
        self.button_send.pack(side=tk.LEFT,fill="both")


        self.recive_content.config(yscrollcommand=self.receive_scrollbar.set)

        # 发送内容区域布局
        self.send_frame = tk.Frame(self.main_window)
        self.send_frame.pack(anchor=tk.SW, padx=10, pady=(0, 10))

        self.send_content = tk.Text(self.send_frame, height=5, width=30)
        self.send_content.config(state=tk.NORMAL)
        self.send_content.pack(side=tk.LEFT)

        self.send_scrollbar = tk.Scrollbar(self.send_frame, orient=tk.VERTICAL, command=self.send_content.yview)
        self.send_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.button_clear = tk.Button(self.send_frame, text="清空\n发送", command=self.clear_send)
        self.button_clear.pack(side=tk.LEFT,fill="y")
        self.button_disconnect = tk.Button(self.send_frame, text="断开", command=self.disconnect)
        self.button_disconnect.pack(side=tk.LEFT,fill="y")
        self.button_more = tk.Button(self.send_frame, text="更多", command=self.more)
        self.button_more.pack(side=tk.LEFT,fill="y")

        self.send_content.config(yscrollcommand=self.send_scrollbar.set)

    def askclose(self,window):
        if window == self.main_window:
            self.ask = askyesno("提示","是否退出程序同时关闭串口？")
            if(self.ask == True):
                if(hasattr(self,"device") and self.device.is_open == True):
                    self.device.close()
                self.main_window.destroy()
                sys.exit(0)
        elif window == self.more_window:
            self.more_window.destroy()
            if hasattr(self,"more_window_is_open") or self.more_window_is_open == True:
                self.more_window_is_open = False
        else:
            showerror("错误","未知的窗口")
        return
    def connect(self):
        if(hasattr(self,"device") == False or self.device.is_open == False):
            try:
                if(self.serial_port.get() == "请选择串口" or self.baund_rate.get() == "请选择波特率"):
                    showerror("错误","配置合适的串口和波特率")
                    return
                self.device = serial.Serial(self.serial_port.get().split("-")[0][:-1],int(self.baund_rate.get()))
                showinfo("提示","串口{}已经连接".format(self.serial_port.get()))
                self.rx = self.create_thread(self.device)
                self.button_connect.configure(fg="green")
            except serial.SerialException as e:
                showerror("错误","串口连接失败\n{}".format(e))
                if(hasattr(self,"device")):
                    self.device.close()
        elif(self.device.is_open):
            showerror("错误","串口已经连接")
            return
        else:
            showerror("错误","串口有未知错误")
    def create_thread(self,device):
        rx = threading.Thread(target=self.receive,args=(device,))
        rx.setDaemon(True)
        rx.start()
        return rx
    def receive(self,device):
        while True:
            if(device.is_open == False):
                break
            try:
                data = device.read(1)
                if(data != b''):
                    self.recive_content.config(state=tk.NORMAL)
                    self.recive_content.insert(tk.END, data.decode())
                    self.recive_content.config(state=tk.DISABLED)
                    self.recive_content.see(tk.END)
            except serial.SerialException as e:
                e.with_traceback()
                break
            except Exception as e:
                print("子线程关闭")
                break
        self.device.close()
    def disconnect(self):
        if(hasattr(self,"device") == False or self.device.is_open == False):
            showerror("错误","串口未连接")
            return
        self.device.close()
        self.button_connect.configure(fg="black")
        showinfo("提示","串口{}已经断开".format(self.serial_port.get()))

    def send(self):
        if(hasattr(self,"device") == False or self.device.is_open == False):
            showerror("错误","串口未连接")
            return
        self.device.write(self.send_content.get("1.0", tk.END).encode())
        
    def clear_recive(self):
        self.recive_content.config(state=tk.NORMAL)
        self.recive_content.delete("1.0", tk.END)
        self.recive_content.config(state=tk.DISABLED)
    def clear_send(self):
        self.send_content.delete("1.0", tk.END)
    def more(self):
        #增加定时发送功能
        #增加自定义语句发送功能
        #增加图像显示功能
        #生成一个新的窗口,用于显示更多功能
        if(hasattr(self,"more_window_is_open") and self.more_window_is_open == True):
            self.askclose(self.more_window)
            self.more_window_is_open = False
            return
        self.more_window_is_open = True
        self.more_window = tk.Toplevel(self.main_window)
        self.more_layout_init()

    def more_layout_init(self):
        self.more_window.title("更多功能")
        self.more_window.resizable(0, 0)
        self.more_window.geometry("+{}+{}".format(self.main_window.winfo_x()+self.main_window.winfo_width(),self.main_window.winfo_y()))
        self.more_window.protocol("WM_DELETE_WINDOW", lambda : self.askclose(self.more_window))
        self.more_window.iconbitmap("icon.ico")

        #定时发送区域布局
        self.timing_send_frame = tk.Frame(self.more_window)
        self.timing_send_frame.pack(side=tk.TOP, padx=10, pady=(0, 10))
        self.timing_send_state = tk.BooleanVar()
        self.timing_send_checkbutton = tk.Checkbutton(self.timing_send_frame, text="定时发送", command=self.timing_send, variable=self.timing_send_state, onvalue=True, offvalue=False)
        self.timing_send_checkbutton.pack(side=tk.LEFT)
        self.timing_send_circle = tk.Entry(self.timing_send_frame, width=10)
        self.timing_send_circle.insert(tk.END, "1000")
        self.timing_send_circle.pack(side=tk.LEFT)
        self.timing_send_label = tk.Label(self.timing_send_frame, text="ms")
        self.timing_send_label.pack(side=tk.LEFT)
        # 自定义语句布局
        
        self.custom_content_frame = tk.Frame(self.more_window)
        self.custom_content_listbox = tk.Listbox(self.custom_content_frame, selectmode=tk.BROWSE)
        self.load_custom_content()
        
        self.custom_content_frame.pack(anchor="nw", padx=10, pady=(0, 10))
        self.custom_content_listbox.pack(side = tk.LEFT)
        # 添加滚动条
        scrollbar = tk.Scrollbar(self.custom_content_frame,command=self.custom_content_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.custom_content_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config()
        self.bind_event_more()
        self.more_layout_tips_init()

        for item in self.custom_content:
            self.custom_content_listbox.insert(tk.END, item)

        self.more_window.mainloop()
    def bind_event_more(self):
        self.custom_content_listbox.bind("<Button-1>",self.more_content_chosen)

    def more_content_chosen(self,event):
        self.send_content.delete("1.0", tk.END)
        cur_selection = self.custom_content_listbox.curselection()
        if cur_selection:
            self.send_content.insert(tk.END, self.custom_content_listbox.get(self.custom_content_listbox.curselection()))

    def more_layout_tips_init(self):
        self.tooltip_timing_send = self.ToolTip(self.timing_send_checkbutton, "定时发送")
        self.tooltip_timing_send_circle = self.ToolTip(self.timing_send_circle, "定时发送时间间隔")

    def load_custom_content(self):
        try:
            self.custom_content = [content for content in open("datas.txt","r",encoding="utf-8").readlines()]
        except Exception as e:
            showerror("错误","未知错误\n"+str(e))
            pass

    def timing_send(self):
        if self.timing_send_state.get() == True:
            if hasattr(self,"device") == False or self.device.is_open == False:
                return
            else:
                self.send()
                self.timing_send_checkbutton.after(self.time_send_circle_ms,self.timing_send)



if __name__ == "__main__":
    app=serial_contact()