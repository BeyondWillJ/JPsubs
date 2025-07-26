import cv2
import os
import numpy as np
from moviepy.editor import VideoFileClip
from PIL import ImageFont, ImageDraw, Image

basic_list = ['133', '166', '什么啊~已经早上了~']
jp_list = ['な', 'ん', 'だ', '~', 'も', 'う', '朝', '…', 'か', 'と', '…']
romaji_list = ['na', 'n', 'da', '~', 'mo', 'u', 'asa', '…', 'ka', 'to', '…']
kana_list = ['', '', '', '', '', '', 'あさ', '', '', '', '']

# 新增：字幕结构体
subtitles = [{
    "start_frame": int(basic_list[0]),
    "end_frame": int(basic_list[1]),
    "cn": basic_list[2],
    "jp": jp_list,
    "romaji": romaji_list,
    "kana": kana_list
}]

# 从CSV读取字幕数据
import csv
subtitles = []
with open("JPsub.csv", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)
    for i in range(0, len(rows), 4):
        if i + 3 < len(rows):
            basic_list = rows[i]
            kana_list = rows[i+1]
            jp_list = rows[i+2]
            romaji_list = rows[i+3]
            # 替换日文和中文中的~为全角～
            cn_text = basic_list[2].replace('~', '～')
            jp_list_fixed = [c.replace('~', '～') for c in jp_list]
            subtitles.append({
                "start_frame": int(basic_list[0]),
                "end_frame": int(basic_list[1]),
                "cn": cn_text,
                "jp": jp_list_fixed,
                "romaji": romaji_list,
                "kana": kana_list
            })

# 进度条依赖
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

FONT_PATH_CN = "msyhbd.ttc"  # 微软雅黑粗体
FONT_PATH_JP = "UDDigiKyokashoN-B.ttc"  # 日文字体（Meiryo，现代日文显示效果佳）
FONT_PATH_ROMAJI = "arialbd.ttf"  # 罗马音粗体
FONT_SIZE_CN = 40
FONT_SIZE_JP = 40
FONT_SIZE_ROMAJI = 22
FONT_SIZE_ROMAJI_SMALL = 20  # 小号罗马音
FONT_SIZE_KANA = 28

def draw_text(img, text, pos, font, fill, anchor=None):
    draw = ImageDraw.Draw(img)
    draw.text(pos, text, font=font, fill=fill, anchor=anchor)

def render_subtitle(frame, subtitle, frame_idx):
    # 转为PIL Image
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    w, h = img_pil.size

    # 字体
    font_cn = ImageFont.truetype(FONT_PATH_CN, FONT_SIZE_CN)
    font_jp = ImageFont.truetype(FONT_PATH_JP, FONT_SIZE_JP)
    font_romaji_default = ImageFont.truetype(FONT_PATH_ROMAJI, FONT_SIZE_ROMAJI)
    font_romaji_small = ImageFont.truetype(FONT_PATH_ROMAJI, FONT_SIZE_ROMAJI_SMALL)
    font_kana = ImageFont.truetype(FONT_PATH_JP, FONT_SIZE_KANA)

    # 居中参数
    line_gap = 4
    # 计算总内容高度
    total_height = FONT_SIZE_KANA + line_gap + FONT_SIZE_JP + line_gap + FONT_SIZE_ROMAJI + line_gap + FONT_SIZE_CN
    y_top = (h - total_height) // 2 - 10  # 整体向上移动30像素，可根据需要调整

    # 假名注音
    jp_text = ''.join(subtitle["jp"])
    romaji_texts = subtitle["romaji"]
    jp_chars = subtitle["jp"]
    kana_texts = subtitle["kana"]
    # 计算每个字的宽度
    font_jp = ImageFont.truetype(FONT_PATH_JP, FONT_SIZE_JP)
    jp_widths = [font_jp.getbbox(c)[2] - font_jp.getbbox(c)[0] for c in jp_chars]
    total_jp_width = sum(jp_widths)
    x_start = w//2 - total_jp_width//2

    # 假名注音（最上）
    y_kana = y_top + FONT_SIZE_KANA // 2
    x = x_start
    for i, kana in enumerate(kana_texts):
        if kana:
            c_width = jp_widths[i]
            # 检查左右是否有训读
            left_has = i > 0 and kana_texts[i-1]
            right_has = i < len(kana_texts)-1 and kana_texts[i+1]
            if left_has or right_has:
                # 统计连续训读组
                group_start = i
                group_end = i
                while group_start > 0 and kana_texts[group_start-1]:
                    group_start -= 1
                while group_end < len(kana_texts)-1 and kana_texts[group_end+1]:
                    group_end += 1
                group_len = group_end - group_start + 1
                group_kana = kana_texts[group_start:group_end+1]
                group_jp_width = sum(jp_widths[group_start:group_end+1])
                # 先用默认字号测量总宽度
                font_kana_tmp = ImageFont.truetype(FONT_PATH_JP, FONT_SIZE_KANA)
                kana_widths = [font_kana_tmp.getbbox(k)[2] - font_kana_tmp.getbbox(k)[0] for k in group_kana]
                total_kana_width = sum(kana_widths)
                # 计算缩放比例
                scale = group_jp_width / total_kana_width if total_kana_width > 0 else 1.0
                # 计算新字号，最小12
                new_font_size = max(int(FONT_SIZE_KANA * scale), 12)
                font_kana_scaled = ImageFont.truetype(FONT_PATH_JP, new_font_size)
                # 重新计算每个训读的宽度
                kana_widths_scaled = [font_kana_scaled.getbbox(k)[2] - font_kana_scaled.getbbox(k)[0] for k in group_kana]
                # 计算基线对齐偏移
                y_offset = (FONT_SIZE_KANA - new_font_size) // 2
                # 绘制整组训读
                x_group = x_start + sum(jp_widths[:group_start])
                x_k = x_group
                for idx, k in enumerate(group_kana):
                    draw_text(img_pil, k, (x_k + kana_widths_scaled[idx]//2, y_kana + y_offset), font_kana_scaled, (0,255,255), anchor="mm")
                    x_k += jp_widths[group_start + idx]
                # 跳过已绘制的组
                if i < group_end:
                    x += sum(jp_widths[i:group_end+1])
                    continue
            else:
                draw_text(img_pil, kana, (x + c_width//2, y_kana), font_kana, (0,255,255), anchor="mm")
        x += jp_widths[i]

    # 日文原文
    y_jp = y_kana + FONT_SIZE_KANA // 2 + line_gap + FONT_SIZE_JP // 2
    draw_text(img_pil, jp_text, (w//2, y_jp), font_jp, (255,255,255), anchor="mm")

    # 罗马音（稍靠上）
    y_romaji = y_jp + FONT_SIZE_JP // 2 + line_gap // 2 + FONT_SIZE_ROMAJI // 2
    x = x_start
    i = 0
    while i < len(romaji_texts):
        roma = romaji_texts[i]
        c = jp_chars[i]
        c_width = jp_widths[i]
        # 检查是否为一组连续长度>=4的罗马音
        if len(roma) >= 4:
            # 找到连续的长度>=4的罗马音组
            group_start = i
            group_end = i
            while group_end + 1 < len(romaji_texts) and len(romaji_texts[group_end + 1]) >= 4:
                group_end += 1
            group_romaji = romaji_texts[group_start:group_end+1]
            group_jp_width = sum(jp_widths[group_start:group_end+1]) + 2
            # 用默认字号测量总宽度
            font_romaji_tmp = ImageFont.truetype(FONT_PATH_ROMAJI, FONT_SIZE_ROMAJI)
            romaji_widths = [font_romaji_tmp.getbbox(r)[2] - font_romaji_tmp.getbbox(r)[0] for r in group_romaji]
            total_romaji_width = sum(romaji_widths)
            # 计算缩放比例
            scale = group_jp_width / total_romaji_width if total_romaji_width > 0 else 1.0
            new_font_size = max(int(FONT_SIZE_ROMAJI * scale), 10)
            font_romaji_scaled = ImageFont.truetype(FONT_PATH_ROMAJI, new_font_size)
            romaji_widths_scaled = [font_romaji_scaled.getbbox(r)[2] - font_romaji_scaled.getbbox(r)[0] for r in group_romaji]
            y_offset = (FONT_SIZE_ROMAJI - new_font_size) // 2
            # 绘制整组
            x_group = x_start + sum(jp_widths[:group_start])
            x_r = x_group
            for idx, r in enumerate(group_romaji):
                draw_text(img_pil, r, (x_r + romaji_widths_scaled[idx]//2, y_romaji + y_offset), font_romaji_scaled, (255,255,0), anchor="mm")
                x_r += jp_widths[group_start + idx]
            i = group_end + 1
            x = x_r
        else:
            font_to_use = font_romaji_default
            y_offset = 0
            draw_text(img_pil, roma, (x + c_width//2, y_romaji + y_offset), font_to_use, (255,255,0), anchor="mm")
            x += c_width
            i += 1

    # 中文（最下）
    y_cn = y_romaji + FONT_SIZE_ROMAJI // 2 + line_gap + FONT_SIZE_CN // 2 + 5  # 中文下移5像素
    draw_text(img_pil, subtitle["cn"], (w//2, y_cn), font_cn, (255,255,255), anchor="mm")

    # 转回OpenCV格式
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def process_video(input_path, output_path, subtitles):
    from moviepy.editor import VideoFileClip
    import cv2
    import numpy as np
    ext_height = 200  # 下方拓展高度

    def add_subtitle_frame(get_frame, t):
        frame = get_frame(t)
        # frame: H x W x 3, uint8, RGB
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        height, width = frame_bgr.shape[:2]
        black_bar = np.zeros((ext_height, width, 3), dtype=np.uint8)
        # 计算当前帧号
        fps = video.fps
        frame_idx = int(round(t * fps))
        sub_to_render = None
        for sub in subtitles:
            if sub["start_frame"] <= frame_idx <= sub["end_frame"]:
                sub_to_render = sub
                break
        if sub_to_render:
            black_bar = render_subtitle(black_bar, sub_to_render, frame_idx)
        out_frame = np.vstack([frame_bgr, black_bar])
        out_frame_rgb = cv2.cvtColor(out_frame, cv2.COLOR_BGR2RGB)
        return out_frame_rgb

    video = VideoFileClip(input_path)
    new_h = video.h + ext_height
    new_w = video.w
    new_video = video.fl(lambda gf, t: add_subtitle_frame(gf, t)).set_audio(video.audio)
    new_video = new_video.set_duration(video.duration)
    new_video = new_video.set_fps(video.fps)
    new_video = new_video.resize((new_w, new_h))
    new_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

if __name__ == "__main__":
    # 批量生成每条字幕的图片，命名为sub起始帧-结束帧.png
    width = 1920
    height = 200  # 固定高度为200，便于拼接
    blank_frame = np.zeros((height, width, 3), dtype=np.uint8)
    for sub in subtitles:
        img = render_subtitle(blank_frame, sub, 0)
        fname = f"sub{sub['start_frame']}-{sub['end_frame']}.png"
        impath = f"subs/{fname}"
        # 确保目录存在
        os.makedirs("subs", exist_ok=True)
        cv2.imwrite(impath, img)
        print(f"已输出图片 {impath}")

    # 处理视频
    name = "chiikawa-11.mp4"  # 输入视频名称
    input_video_path = name
    # name_o.mp4
    output_video_path = f"{name.replace('.mp4', '')}-o.mp4"
    process_video(input_video_path, output_video_path, subtitles)
    print(f"已处理视频，输出到 {output_video_path}")
