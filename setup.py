from setuptools import setup, find_packages

setup(
    name="gpiocom",
    version="0.1.3",
    author="Florian Töns",
    description="Schnelle GPIO-Kommunikation für Raspberry Pi",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/limo123123/gpiocom",
    packages=find_packages(),
    install_requires=[
        "pigpio>=1.78",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
