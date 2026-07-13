with open("diff.txt", "r", encoding="utf-16le") as f:
    content = f.read()

with open("diff_utf8.txt", "w", encoding="utf-8") as f:
    f.write(content)
