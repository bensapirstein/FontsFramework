from setuptools import setup

setup(
    name='FontsFramework',  # Replace with your project name
    version='0.1',
    install_requires=['ufo-extractor', 'ufo2ft', 'arabic-reshaper',
                      'fontTools', 'defcon', 'svgpath2mpl', 'python-bidi',
                      'tqdm', 
                      'pysilfont @ git+https://github.com/silnrsi/pysilfont'],
)
