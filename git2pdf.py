# -*- coding: UTF-8 -*-
# !/usr/bin/env python

import os
import sys
import subprocess
import time

languages = {
    "python": {
        "language": "python",
        "extensions": [".py"],
    },
    "c++": {
        "language": "cpp",
        "extensions": [".cpp", ".cc", ".h", ".hpp", ".hh"],
    },
    "go":  {
        "language": "go",
        "extensions": [".go"],
    },
    "pascal": {
        "language": "pascal",
        "extensions": [".pas"],
    },
    "c#": {
        "language": "cpp",
        "extensions": [".cs"],
    },
    "d": {
        "language": "cpp",
        "extensions": [".d"],
    },
    "js": {
        "language": "js",
        "extensions": [".js"],
    },
}

if len(sys.argv) < 3:
    sys.exit("Not enough arguments!")

if sys.argv[2].endswith(".git"):
    project = sys.argv[2].split("/")[-1].split(".git")[0] if '/' in sys.argv[2] else sys.argv[2]
else:
    project = sys.argv[2]
language = languages[sys.argv[1]]["language"]
extensions = languages[sys.argv[1]]["extensions"]
text = ""

if not os.path.isdir(project):
    print("Fetching project: " + project)
    cmd = subprocess.Popen(["git", "clone", "--depth", "1", sys.argv[2]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (status, error) = cmd.communicate()
    if cmd.poll() != 0:
        sys.exit("Failed fetching project!")

file_path = None
readme = ""
if os.path.isfile(os.path.join(project, "README.md")):
    file_path = os.path.join(project, "README.md")
elif os.path.isfile(os.path.join(project, "README.rst")):
    file_path = os.path.join(project, "README.rst")
if file_path:
    with open(file_path, 'r') as f:
        readme += f.read().strip() + "\n\n"
    cmd = subprocess.Popen(["markdown", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (status, error) = cmd.communicate()
    if cmd.poll() != 0:
        sys.exit("Failed converting to readme.html!")
    with open("readme.html", "w") as f:
        f.write(status)
    cmd = subprocess.Popen(["wkhtmltopdf", "--user-style-sheet", "custom.css", "readme.html", "readme.pdf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (status, error) = cmd.communicate()
    if cmd.poll() != 0:
        sys.exit("Failed converting to readme.pdf!")

for root, subdirs, files in os.walk(project):
    for file_ in files:
        if not any([True if file_.endswith(ext) else False for ext in extensions]):
            continue
        file_path = os.path.join(root, file_)
        print("Found matching file in project:" + os.path.join(root, file_))
        with open(file_path, 'r') as f:
            text += "#\n" + "# " + file_path + "\n#\n\n"
            text += f.read().strip() + "\n\n"

print("Saving to text file ...")
with open(project + ".txt", "w") as f:
    f.write(text)

print("Converting to html ...")
cmd = subprocess.Popen(["code2html", "-n", "-l", language, "-w", "120", project + ".txt", project + ".html"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(project)
(status, error) = cmd.communicate()
if cmd.poll() != 0:
    sys.exit("Failed converting to html!")
text = ""
with open(project + ".html", "r") as f:
    text = f.read()
with open(project + ".html", "w") as f:
    f.write(text.replace("</body>", "<br />" + sys.argv[2] + "\n</body>"))

print("Converting to pdf ...")
if readme:
    cmd = subprocess.Popen(["wkhtmltopdf", "--user-style-sheet", "custom.css", project + ".html", project + "_.pdf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
else:
    cmd = subprocess.Popen(["wkhtmltopdf", "--user-style-sheet", "custom.css", project + ".html", project + ".pdf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(status, error) = cmd.communicate()
if cmd.poll() != 0:
    sys.exit("Failed converting to pdf!")

if readme:
    cmd = subprocess.Popen(["pdfunite", "readme.pdf", project + "_.pdf", project + ".pdf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (status, error) = cmd.communicate()
    if cmd.poll() != 0:
        sys.exit("Failed merging readme to pdf!")

os.remove(project + '.html')
os.remove(project + '.txt')
if readme:
    os.remove(project + '_.pdf')
    os.remove('readme.html')
    os.remove('readme.pdf')

sys.exit("Done.")