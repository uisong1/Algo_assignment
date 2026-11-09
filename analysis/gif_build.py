import sys, glob, subprocess
from PIL import Image
src, name, dur, width = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
fs = sorted(glob.glob(f'{src}/f*.png'))
W = max(Image.open(f).width for f in fs) + 48; H = max(Image.open(f).height for f in fs) + 40
import os; pd = f'pad_{name}'; os.makedirs(pd, exist_ok=True)
L = []
for k, f in enumerate(fs):
    c = Image.new('RGB', (W, H), (255, 255, 255)); c.paste(Image.open(f).convert('RGB'), (24, 20)); c.save(f'{pd}/p{k:03d}.png')
    d = (2.5 if name == 'steps' else 2.0) if k == 0 else ((4.5 if name == 'steps' else 4.0) if k == len(fs) - 1 else dur)
    L.append(f"file '{pd}/p{k:03d}.png'\nduration {d}")
L.append(f"file '{pd}/p{len(fs)-1:03d}.png'")
open(f'list_{name}.txt', 'w').write("\n".join(L) + "\n")
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",f"list_{name}.txt","-vf",
  f"fps=10,scale={width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=none:diff_mode=rectangle",
  "-loop","0",f"lis_{name}.gif"], check=True)
print(name, len(fs), "frames")
