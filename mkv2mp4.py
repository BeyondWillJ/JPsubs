import os
import subprocess

def mkv_to_mp4(folder):
    for filename in os.listdir(folder):
        if filename.lower().endswith('.mkv'):
            mkv_path = os.path.join(folder, filename)
            mp4_path = os.path.splitext(mkv_path)[0] + '.mp4'
            # ffmpeg command: copy video/audio streams, no re-encoding
            cmd = [
                'ffmpeg',
                '-i', mkv_path,
                '-c', 'copy',
                mp4_path
            ]
            print(f'Converting: {mkv_path} -> {mp4_path}')
            subprocess.run(cmd, check=True)

if __name__ == '__main__':
    folder = os.path.dirname(os.path.abspath(__file__))
    mkv_to_mp4(folder)