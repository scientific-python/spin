import subprocess


def run(cmd):
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd)
