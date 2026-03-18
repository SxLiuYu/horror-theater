#!/usr/bin/env python3
"""
阿里云百炼 - 通义万相文生视频
使用官方 dashscope SDK

运行前：
1. pip install dashscope
2. 设置环境变量 DASHSCOPE_API_KEY=sk-xxx
"""

from http import HTTPStatus
from dashscope import VideoSynthesis
import dashscope
import os
import requests

# 配置 API
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
api_key = os.getenv("DASHSCOPE_API_KEY", "sk-16cb5f2bc07a4984b43588a6f7e1c4c6")

# 76 场场景提示词（从分镜脚本提取）
SCENES = [
    # 第 1 集 - 下载 (6 场)
    {"name": "E01_S01_黑屏警告", "prompt": "黑色屏幕，红色警告文字闪烁：'警告：检测到非法程序'，恐怖氛围，故障艺术风格", "duration": 5},
    {"name": "E01_S02_陆离卧室", "prompt": "一个 21 岁中国黑发青年男性，戴眼镜，穿深蓝色连帽卫衣，清晨在卧室醒来，阳光透过窗帘，伸手拿床头柜上的手机，日式动画风格，吉卜力工作室风格，柔光", "duration": 5},
    {"name": "E01_S03_手机界面", "prompt": "手机屏幕特写，黑色 APP 图标，红色眼睛图案，诡异光芒，UI 界面设计，恐怖风格", "duration": 4},
    {"name": "E01_S04_地铁车厢", "prompt": "深夜空荡地铁车厢，冷白色灯光，一个青年独自坐着，窗外黑暗，悬疑氛围，动画风格", "duration": 5},
    {"name": "E01_S05_小区入口", "prompt": "老旧小区入口，夜晚，昏黄路灯，铁门生锈，阴影浓重，恐怖动画风格", "duration": 5},
    {"name": "E01_S06_电梯走廊", "prompt": "昏暗楼道走廊，绿色墙裙剥落，感应灯闪烁，电梯门紧闭，压抑氛围", "duration": 4},
    
    # 第 2 集 - 娃娃 (6 场)
    {"name": "E02_S01_陆离惊醒", "prompt": "青年从床上惊醒，冷汗，清晨微光，惊恐表情，特写镜头，动画风格", "duration": 4},
    {"name": "E02_S02_娃娃特写", "prompt": "破旧布娃娃特写，黑色纽扣眼睛，诡异笑容，缝线粗糙，恐怖特写", "duration": 5},
    {"name": "E02_S03_苏晓登场", "prompt": "20 岁中国女孩，棕色齐肩短发，橙色毛衣，白色裤子，灿烂笑容，校园背景，晴天，新海诚风格", "duration": 5},
    {"name": "E02_S04_教室讨论", "prompt": "大学教室，几个学生围坐讨论，黑板写满笔记，阳光从窗户照入，日常动画风格", "duration": 5},
    {"name": "E02_S05_娃娃移动", "prompt": "娃娃自己移动位置，模糊残影，诡异氛围，慢镜头，恐怖动画", "duration": 4},
    {"name": "E02_S06_小太阳 APP", "prompt": "手机 APP 界面，可爱 AI 助手形象，温暖黄色光芒，UI 动效，治愈风格", "duration": 4},
    
    # 第 3 集 - 闯入者 (6 场)
    {"name": "E03_S01_深夜敲门", "prompt": "深夜公寓门，敲门声，门缝透光，紧张氛围，第一人称视角", "duration": 4},
    {"name": "E03_S02_苏晓求助", "prompt": "女孩站在门口，害怕表情，抱着娃娃，夜晚楼道灯光，动画风格", "duration": 5},
    {"name": "E03_S03_客厅对话", "prompt": "小客厅，两人对坐，暖色台灯，热茶冒气，温馨氛围，室内场景", "duration": 5},
    {"name": "E03_S04_娃娃眼睛发光", "prompt": "娃娃眼睛发出红光，黑暗房间，诡异光芒，特写镜头，恐怖风格", "duration": 4},
    {"name": "E03_S05_影子异动", "prompt": "墙上影子自己移动，与实物不符，诡异扭曲，恐怖氛围", "duration": 4},
    {"name": "E03_S06_超度光芒", "prompt": "温暖白色光芒，鬼魂化作光点消散，平静表情，柔焦，治愈氛围，黄金时刻灯光", "duration": 5},
    
    # 继续生成更多场景...
]

def generate_video():
    print("🎬 开始生成视频...")
    print(f"   模型：wan2.6-t2v")
    print(f"   提示词：{PROMPT[:50]}...")
    print()
    
    # 异步调用
    rsp = VideoSynthesis.async_call(
        api_key=api_key,
        model='wan2.6-t2v',
        prompt=PROMPT,
        size='1280*720',
        duration=5,
        prompt_extend=True,
        watermark=False
    )
    
    print(f"提交响应：{rsp}")
    
    if rsp.status_code == HTTPStatus.OK:
        task_id = rsp.output.task_id
        print(f"✅ Task ID: {task_id}")
    else:
        print(f'❌ 失败：{rsp.status_code}, {rsp.code}, {rsp.message}')
        return
    
    # 等待完成
    print("\n⏳ 等待生成完成（最多 10 分钟）...")
    rsp = VideoSynthesis.wait(task=rsp, api_key=api_key)
    
    if rsp.status_code == HTTPStatus.OK:
        video_url = rsp.output.video_url
        print(f"\n✅ 生成成功！")
        print(f"📥 视频 URL: {video_url}")
        
        # 下载视频
        save_path = "output_aliyun.mp4"
        print(f"📥 下载视频到：{save_path}")
        video_data = requests.get(video_url).content
        with open(save_path, "wb") as f:
            f.write(video_data)
        print(f"✅ 已保存：{save_path}")
        print(f"   大小：{len(video_data) / 1024 / 1024:.2f} MB")
    else:
        print(f'❌ 失败：{rsp.status_code}, {rsp.code}, {rsp.message}')


if __name__ == '__main__':
    generate_video()
