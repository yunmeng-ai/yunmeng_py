# yunmeng_py
###图书馆智能助手系统

##项目概述
这是一个完整的图书馆智能助手系统，包含上位机GUI应用、下位机嵌入式控制程序和串口通信模块，实现图书位置查询和自动导航功能。

#系统工作流程：

1.用户通过GUI查询图书位置
2.系统解析图书所在区域（A-F）
3.通过串口发送导航指令给下位机
4.下位机控制小车移动到指定区域
##功能特点

#上位机功能
• 图书位置查询与展示
• 用户友好的图形界面
• 实时对话交互
• 字体大小调整
• 热门话题快速访问
• 导航指令生成与发送

#下位机功能
• 四电机PID精确控制
• 编码器速度反馈
• 前进/后退双PWM控制
• 电机自动校准
• 速度同步算法

#通信功能
• 16进制指令传输
• 错误检测与处理
• 响应接收与解析

#文件结构
Library-Assistant/
├── library_core.py          # 核心逻辑：图书数据处理与API交互
├── library_gui.py           # Tkinter图形用户界面
├── main.py                  # 程序入口
├── serial_communicator.py   # 串口通信模块
├── pwm_test.c               # 下位机电机控制程序
└── pwm_test.h               # 下位机头文件

硬件要求

上位机：
Python 3.7+
支持串口通信的计算机

下位机：
STM32F4系列开发板
4个带编码器的直流电机
电机驱动模块
USB转TTL串口模块

##安装与使用
#上位机安装
pip install tkinter requests pyserial
python main.py

#下位机部署
将pwm_test.c和pwm_test.h添加到RT-Thread工程
配置PWM和编码器设备
编译烧录到目标设备

#使用说明
启动上位机GUI
通过搜索框查询图书
点击"带我去找书"按钮
系统自动导航到图书所在区域

#串口通信协议
命令格式：

区域代码（单字节ASCII）：'A'-'F'

#示例：

导航到A区：发送41（十六进制）

导航到B区：发送42（十六进制）

#开发与贡献
欢迎贡献代码！请遵循以下流程：

Fork仓库

创建新分支（git checkout -b feature/your-feature）

提交修改（git commit -am 'Add some feature'）

推送到分支（git push origin feature/your-feature）

创建Pull Request

#许可证
本项目采用MIT许可证。
