import requests
import bs4
import sys
from os import path, makedirs

# http://images.google.com/search?q=knife&sout=1&tbm=isch&ei=OpJCW-ubCoWJwgTZyr-YBA&start=0&sa=N


def main():
    if len(sys.argv) < 4:
        print("Use: {} <keyword> <amount of images> <output path>".format(sys.argv[0]))
        return

    keyword = sys.argv[1]

    try:
        amount = int(sys.argv[2])

        if amount <= 0:
            print("Invalid parameter: amount")
            return
    except ValueError as err:
        print(err)
        return

    output_path = sys.argv[3]

    if not path.exists(output_path):
        try:
            makedirs(output_path)
        except OSError as err:
            print(err.strerror)
            return

    page = 0

    imgs = list()
    total = 0
    while total < amount:
        req = requests.get(
            f"http://images.google.com/search?q={keyword}&sout=1&tbm=isch&ei=OpJCW-ubCoWJwgTZyr-YBA&start={page}&sa=N")
        bs = bs4.BeautifulSoup(req.text, "html.parser")
        table = bs.find(class_="images_table")

        if table is not None:
            imgs.extend(table.find_all("img"))
        else:
            print("Failed to get images...")
            return
        page += 10

        if len(imgs) > amount:
            imgs = imgs[:amount]

        total = len(imgs)
        print(f"[+]{total}/{amount}")
    ext = ""
    count = 0

    imgs_ext = {b'\xff\xd8\xff\xe0': ".jpg",
                b'\x42\x4d\x00\x00': ".bmp",
                b'\x89\x50\x4E\x47': ".png",
                b'\x49\x49\x2A\x00': ".tiff"}


    total_bytes = 0

    print("Downloading...")

    for n in range(amount):
        url = imgs[n]
        try:
            req = requests.get(url.get("src"), stream=True)
            file_sig = req.content[:4]

            if file_sig in imgs_ext:
                ext = imgs_ext[file_sig]

            filename = keyword + str(n) + ext
            file_path = path.join(output_path, filename)

            with open(file_path, "wb") as file:
                for data in req.iter_content(chunk_size=1024):
                    file.write(data)
                    total_bytes += len(data)

        except Exception as err:
            print(err)

    print(f"[!]Total bytes: {total_bytes}")
    print("Done")


if __name__ == '__main__':
    main()
