from defcon import Font
import extractor

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

