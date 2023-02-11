from ufo2ft import compileOTF
from defcon import Font

def ufo_to_ttf(ufo_file_path, ttf_file_path):
    ufo = Font(ufo_file_path)
    otf = compileOTF(ufo)
    otf.save(ttf_file_path)

if "__main__" == __name__:
    # ufo_to_ttf("../../../data/processed/fonts/UFO/Alef/Alef-Regular.ufo", "Alef-Regular.ttf")
    ufo_to_ttf("Alef-Regular.ufo", "Alef-Regular.ttf")