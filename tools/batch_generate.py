#!/usr/bin/env python3
"""
阿里云百炼 - 批量生成视频
使用 wanx2.1-t2v-turbo 模型（200 秒免费额度）
"""

from http import HTTPStatus
from dashscope import VideoSynthesis
import dashscope
import os
import requests
import time
import json

# 配置 API
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
api_key = os.getenv("DASHSCOPE_API_KEY", "sk-16cb5f2bc07a4984b43588a6f7e1c4c6")

# 76 场场景提示词（精简版 - 第 1-2 集）
SCENES = [
    # 第 1 集《下载》- 6 场
    {"name": "E01_S01_黑屏警告", "prompt": "黑色屏幕，红色警告文字闪烁：'警告：检测到非法程序'，恐怖氛围，故障艺术风格", "duration": 5},
    {"name": "E01_S02_陆离卧室", "prompt": "一个 21 岁中国黑发青年男性，戴眼镜，穿深蓝色连帽卫衣，清晨在卧室醒来，阳光透过窗帘，伸手拿床头柜上的手机，日式动画风格，吉卜力工作室风格，柔光", "duration": 5},
    {"name": "E01_S03_手机界面", "prompt": "手机屏幕特写，黑色 APP 图标，红色眼睛图案，诡异光芒，UI 界面设计，恐怖风格", "duration": 4},
    {"name": "E01_S04_地铁车厢", "prompt": "深夜空荡地铁车厢，冷白色灯光，一个青年独自坐着，窗外黑暗，悬疑氛围，动画风格", "duration": 5},
    {"name": "E01_S05_小区入口", "prompt": "老旧小区入口，夜晚，昏黄路灯，铁门生锈，阴影浓重，恐怖动画风格", "duration": 5},
    {"name": "E01_S06_电梯走廊", "prompt": "昏暗楼道走廊，绿色墙裙剥落，感应灯闪烁，电梯门紧闭，压抑氛围", "duration": 4},
    
    # 第 2 集《娃娃》- 6 场
    {"name": "E02_S01_陆离惊醒", "prompt": "青年从床上惊醒，冷汗，清晨微光，惊恐表情，特写镜头，动画风格", "duration": 4},
    {"name": "E02_S02_娃娃特写", "prompt": "破旧布娃娃特写，黑色纽扣眼睛，诡异笑容，缝线粗糙，恐怖特写", "duration": 5},
    {"name": "E02_S03_苏晓登场", "prompt": "20 岁中国女孩，棕色齐肩短发，橙色毛衣，白色裤子，灿烂笑容，校园背景，晴天，新海诚风格", "duration": 5},
    {"name": "E02_S04_教室讨论", "prompt": "大学教室，几个学生围坐讨论，黑板写满笔记，阳光从窗户照入，日常动画风格", "duration": 5},
    {"name": "E02_S05_娃娃移动", "prompt": "娃娃自己移动位置，模糊残影，诡异氛围，慢镜头，恐怖动画", "duration": 4},
    {"name": "E02_S06_小太阳 APP", "prompt": "手机 APP 界面，可爱 AI 助手形象，温暖黄色光芒，UI 动效，治愈风格", "duration": 4},
]

def generate_scene(scene, index, total):
    """生成单个场景"""
    print(f"\n[{index}/{total}] {scene['name']}")
    print(f"   提示词：{scene['prompt'][:50]}...")
    
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
            print(f"   ❌ 提交失败：{rsp.code} - {rsp.message}")
            return None
        
        task_id = rsp.output.task_id
        print(f"   ✅ Task ID: {task_id}")
        
        # 等待完成
        print(f"   ⏳ 等待生成...", end="")
        rsp = VideoSynthesis.wait(task=rsp, api_key=api_key)
        
        if rsp.status_code != HTTPStatus.OK:
            print(f"\n   ❌ 生成失败：{rsp.code} - {rsp.message}")
            return None
        
        video_url = rsp.output.video_url
        print(f" 完成！")
        
        # 下载视频
        save_path = f"output_{scene['name']}.mp4"
        video_data = requests.get(video_url).content
        with open(save_path, "wb") as f:
            f.write(video_data)
        
        size_mb = len(video_data) / 1024 / 1024
        print(f"   📥 已保存：{save_path} ({size_mb:.2f} MB)")
        
        return {
            "name": scene['name'],
            "task_id": task_id,
            "video_url": video_url,
            "save_path": save_path,
            "size_mb": size_mb
        }
        
    except Exception as e:
        print(f"   ❌ 错误：{e}")
        return None


def batch_generate():
    """批量生成所有场景"""
    print("🎬 批量视频生成")
    print("="*60)
    print(f"   模型：wanx2.1-t2v-turbo")
    print(f"   免费额度：200 秒")
    print(f"   场景数量：{len(SCENES)}")
    print(f"   预计消耗：{sum(s['duration'] for s in SCENES)} 秒")
    print("="*60)
    
    results = []
    
    for i, scene in enumerate(SCENES, 1):
        result = generate_scene(scene, i, len(SCENES))
        if result:
            results.append(result)
        
        # 保存进度
        with open("batch_progress.json", "w", encoding="utf-8") as f:
            json.dump({
                "total": len(SCENES),
                "completed": len(results),
                "results": results
            }, f, ensure_ascii=False, indent=2)
        
        # 避免 API 限流
        if i < len(SCENES):
            print(f"   ⏸️  等待 3 秒...")
            time.sleep(3)
    
    # 最终报告
    print("\n" + "="*60)
    print("📊 批量生成完成！")
    print(f"   总场景：{len(SCENES)}")
    print(f"   成功：{len(results)}")
    print(f"   失败：{len(SCENES) - len(results)}")
    print(f"   总大小：{sum(r['size_mb'] for r in results):.2f} MB")
    print("="*60)


if __name__ == '__main__':
    batch_generate()
