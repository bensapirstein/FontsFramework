from defcon import Font
import extractor
#from ufo2ft import compileOTF

def ttf_to_ufo(ttf_file_path: str, ufo_file_path: str):

    # Convert TTF file to UFO
    ufo = Font()
    try:
        extractor.extractUFO(ttf_file_path, ufo)
    except Exception as e:
        print(e)
        print(f"While parsing {ttf_file_path}")

    ufo.save(ufo_file_path)

def var_ttf_to_ufo(ttf_file_path: str, ufo_file_path: str):
    # TODO: Change the implementation to fit variable fonts
    # Convert TTF file to UFO
    ufo = Font()
    try:
        extractor.extractUFO(ttf_file_path, ufo)
    except Exception as e:
        print(e)
        print(f"While parsing {ttf_file_path}")

    ufo.save(ufo_file_path)

def ufo_to_ttf(ufo_file_path, ttf_file_path):
    ufo = Font(ufo_file_path)
    otf = compileOTF(ufo)
    otf.save(ttf_file_path)