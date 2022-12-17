from setuptools import setup

setup(
    name='your_project_name',  # Replace with your project name
    version='0.1',
    packages=['your_package_name'],  # Replace with your package name
    install_requires=['ufo-extractor', 'fontTools', 'defcon'],
    author='Your Name',  # Replace with your name
    author_email='your@email.com',  # Replace with your email address
    description='A brief description of your project',
    entry_points={
        'console_scripts': [
            'your_script_name=your_package_name.your_module_name:main',  # Replace with your script name and module name
        ],
    },
)
