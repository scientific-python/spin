import subprocess


def run_devpy(extra_args):
    p = subprocess.run(["python", "-m", "devpy"] + extra_args, capture_output=True)
    if p.returncode != 0:
        print(p.stdout.decode("utf-8"), end="")
        print(p.stderr.decode("utf-8"), end="")
        raise RuntimeError("Failed to execute dev.py; see printed stdout/stderr")
    return p
