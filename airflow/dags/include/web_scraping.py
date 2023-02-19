import urllib

from bs4 import *
import requests
import os
import re


# CREATE FOLDER
def handle_fonts(links, urlLink, folder_name):
    # image downloading start
    download_fonts(links, folder_name, urlLink)


# DOWNLOAD ALL FONTS FROM THAT URL
def download_fonts(links: list, folder_name: str, urlLink: str):
    # initial count is zero
    count = 0

    # print total fonts found in URL
    print(f"Total {len(links)} Font Found!")

    # checking if fonts is not zero
    if len(links) != 0:
        for i, font in enumerate(links):
            # From font tag ,Fetch font Source URL
            try:
                # In font tag ,searching for "data-srcset"
                supported_fonts_extension = ["woff", "woff2", "ttf", "otf"]
                font_link = font["href"]
                if not any(substring in font_link for substring in supported_fonts_extension):
                    continue
                else:
                    regex = re.compile(r'https?:\/\/([^\/]*)')
                    regObj = regex.findall(font_link)
                    if regObj:
                        print("valid url")
                    else:
                        font_link = urlLink + font_link

            # then we will search for "data-src" in img
            # tag and so on..
            except:
                pass

            # After getting Font Source URL
            # We will try to get the content of font
            try:
                r = requests.get(font_link).content
                try:

                    # possibility of decode
                    r = str(r, 'utf-8')

                except UnicodeDecodeError:

                    # After checking above condition, Image Download start
                    index = font_link.rfind('.')
                    font_extension = font_link[index + 1:]
                    with open(f"{folder_name}/fonts{i + 1}." + font_extension, "wb+") as f:
                        f.write(r)

                    # counting number of font downloaded
                    count += 1
            except:
                pass

        # There might be possible, that all
        # fonts not download
        # if all fonts download
        if count == len(links):
            print("All Fonts Downloaded!")

        # if all fonts not download
        else:
            print(f"Total {count} Fonts Downloaded Out of {len(links)} links that found")


# MAIN FUNCTION START
def download_fonts_from_url(url: str, output_folder: str):
    # content of URL
    r = requests.get(url)

    # Parse HTML Code
    soup = BeautifulSoup(r.text, 'html.parser')

    # find all  in URL
    links = soup.findAll('link')
    # Call folder create function
    handle_fonts(links, url, output_folder)