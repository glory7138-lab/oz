import os

def find_file(filename, search_paths):
    found = []
    for sp in search_paths:
        if not os.path.exists(sp):
            continue
        for root, dirs, files in os.walk(sp):
            if filename in files:
                found.append(os.path.join(root, filename))
            if root.count(os.sep) - sp.count(os.sep) >= 4:
                dirs.clear()
    return found

paths = [
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\Users\hyungseok4.kim\AppData",
    r"C:\nvm",
    r"D:\nvm",
    r"D:\Program Files"
]

print("Searching node.exe...")
results = find_file("node.exe", paths)
print("Results:", results)
