#!/usr/bin/env python3
"""Write display-size copies of people photos and project logos.

The homepage shows people photos at 150x150 and carousel logos at 70px tall.
This writes copies at twice those sizes into profile_images/web/ and
logo_pictures/web/ (same file names), leaving the originals untouched.
Run from the repository root after adding or replacing an image:

    python3 _tools/make_web_images.py
"""
import json
import os
import sys

import yaml
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name):
    with open(os.path.join(ROOT, "_data", name)) as f:
        return yaml.safe_load(f)


def resize(src, dst, box, cover):
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    if cover:
        side = min(im.size)
        target = min(side, box[0])
        im = ImageOps.fit(im, (target, target), Image.LANCZOS)
    else:
        im.thumbnail(box, Image.LANCZOS)
    ext = os.path.splitext(dst)[1].lower()
    if ext in (".jpg", ".jpeg"):
        im.convert("RGB").save(dst, quality=82, optimize=True, progressive=True)
    elif ext == ".png":
        im.save(dst, optimize=True)
    else:
        im.save(dst)


def main():
    jobs = []
    for division in load("people.yml"):
        for person in division.get("people", []):
            if person.get("image") and not division.get("alumni"):
                jobs.append(("profile_images", person["image"], (300, 300), True))
    for project in load("projects.yml"):
        if project.get("image"):
            jobs.append(("logo_pictures", project["image"], (500, 140), False))
    for folder, name, box, cover in jobs:
        src = os.path.join(ROOT, folder, name)
        if not os.path.exists(src):
            sys.exit(f"missing source image: {folder}/{name}")
        if name.lower().endswith(".svg"):
            continue
        out_dir = os.path.join(ROOT, folder, "web")
        os.makedirs(out_dir, exist_ok=True)
        dst = os.path.join(out_dir, name)
        resize(src, dst, box, cover)
        print(f"{folder}/{name}: {os.path.getsize(src)//1024} KB -> {os.path.getsize(dst)//1024} KB")


if __name__ == "__main__":
    main()
