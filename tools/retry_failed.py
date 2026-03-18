#!/usr/bin/env python3
"""
重试失败的场景
"""

from http import HTTPStatus
from dashscope import VideoSynthesis
import dashscope
import os
import requests
import json

api_key = os.getenv("DASHSCOPE_API_KEY", "sk-16cb5f2bc07a4984b43588a6f7e1c4c6")
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

# 失败的场景
FAILED_SCENES = [
    {"name": "E01_S03_手机界面", "prompt": "手机屏幕特写，黑色 APP 图标，红色眼睛图案，诡异光芒，UI 界面设计，恐怖风格", "duration": 4},
    {"name": "E01_S06_电梯走廊", "prompt": "昏暗楼道走廊，绿色墙裙剥落，感应灯闪烁，电梯门紧闭，压抑氛围", "duration": 4},
    {"name": "E02_S01_陆离惊醒", "prompt": "青年从床上惊醒，冷汗，清晨微光，惊恐表情，特写镜头，动画风格", "duration": 4},
    {"name": "E02_S05_娃娃移动", "prompt": "娃娃自己移动位置，模糊残影，诡异氛围，慢镜头，恐怖动画", "duration": 4},
    {"name": "E02_S06_小太阳 APP", "prompt": "手机 APP 界面，可爱 AI 助手形象，温暖黄色光芒，UI 动效，治愈风格", "duration": 4},
]

print("🔄 重试失败的场景...")
print("="*60)

for scene in FAILED_SCENES:
    print(f"\n{scene['name']}")
    
    try:
        rsp = VideoSynthesis.async_call(
            api_key=api_key,
            model='wanx2.1-t2v-turbo',
            prompt=scene['prompt'],
            size='1280*720',
            duration=scene['duration'],
            prompt_extend=True,
            watermark=False
        )
        
        if rsp.status_code != HTTPStatus.OK:
            print(f"   ❌ 提交失败：{rsp.message}")
            continue
        
        print(f"   ⏳ 等待生成...", end="")
        rsp = VideoSynthesis.wait(task=rsp, api_key=api_key)
        
        if rsp.status_code != HTTPStatus.OK:
            print(f"\n   ❌ 生成失败：{rsp.message}")
            continue
        
        video_url = rsp.output.video_url
        if not video_url:
            print(f"\n   ❌ 返回空 URL")
            continue
            
        print(f" 完成！")
        
        save_path = f"output_{scene['name']}.mp4"
        video_data = requests.get(video_url).content
        with open(save_path, "wb") as f:
            f.write(video_data)
        
        print(f"   📥 已保存：{save_path} ({len(video_data)/1024/1024:.2f} MB)")
        
    except Exception as e:
        print(f"   ❌ 错误：{e}")

print("\n" + "="*60)
print("重试完成！")
