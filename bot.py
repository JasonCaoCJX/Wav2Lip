# import torch
# x = torch.rand(5, 3)
# print(torch.__version__)
# print(torch.cuda.is_available())

import discord
from discord.ext import commands
import asyncio
import os

bot = commands.Bot(command_prefix='!')

# 创建一个队列来存储待处理的视频请求
video_queue = asyncio.Queue()
# 设置同时处理的最大视频数量
max_videos = 2

async def process_video(video_file, audio_file):
    # 执行你的服务逻辑，处理视频和音频文件
    # 等待生成视频完成
    await asyncio.sleep(60)  # 这里使用sleep来模拟生成视频的时间

    # 将结果发送给用户
    # 你可以根据需要进行逻辑处理，例如将生成的视频发送给用户
    print(f'视频 {video_file} 已生成')

    # 从队列中取出下一个视频请求并处理
    if not video_queue.empty():
        next_video = await video_queue.get()
        await process_video(*next_video)

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

@bot.command()
async def process(ctx, video_file, audio_file):
    # 将视频请求加入队列
    await video_queue.put((video_file, audio_file))
    await ctx.send('视频生成任务已加入队列！')

    # 如果队列中只有一个任务，立即开始处理
    if video_queue.qsize() == 1:
        await process_video(video_file, audio_file)
    else:
        position = video_queue.qsize() - 1  # 计算用户在队列中的位置
        await ctx.send(f'您的视频正在排队等待处理，当前排队位置：{position}')

bot.run('YOUR_BOT_TOKEN')
