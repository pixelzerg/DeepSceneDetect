import os
import subprocess
from typing import List

DIR_ROOT = "data"
DIR_INPUT = os.path.join(DIR_ROOT, "input")
DIR_CLIPS = os.path.join(DIR_ROOT, "clips")
DIR_OUT = os.path.join(DIR_ROOT, "out")
DIR_TMP = os.path.join(DIR_ROOT, "tmp")

def run(command):
    print("> " + str(command))
    subprocess.run(command, shell=True)

def run_out(command):
    print("> " + str(command))
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    output = result.stdout.decode('utf-8').rstrip()
    print("= " + str(output))
    return output

def get_length(path):
    # https://superuser.com/a/945604/581663
    return float(run_out("ffprobe -v error -show_entries "
                         "format=duration -of default=noprint_wrappers=1:nokey=1 \"{}\""
                         .format(path)))

def get_resolution(path):
    # https://superuser.com/a/841379/581663
    return run_out("ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 \"{}\""
                   .format(path))

def get_num_clips() -> int:
    return len(os.listdir(DIR_CLIPS))


def ffmpeg_concat(files: List[str], out_file: str):
    with TmpFile(os.path.join(DIR_TMP, "list.txt")) as list_file:
        with open(list_file, "w") as f:
            for file in files:
                f.write("file '" + os.path.abspath(str(file)) + "'\n")

        run("ffmpeg -y -f concat -safe 0 -i \"{}\" -c copy \"{}\"".format(list_file, out_file))

class TmpFile:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        # create containing directory if not already exist
        os.makedirs(os.path.split(self.path)[0], exist_ok=True)
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        # delete temp file if exists
        if os.path.isfile(self.path):
            os.remove(self.path)
