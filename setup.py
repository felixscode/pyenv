from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
    setup(
        name="pyenv",
        version="0.0.1",
        author="Felix Schelling",
        author_email="felixschelling@gmx.de",
        description="venv wrapper",
        long_description=long_description,
        url="<github url where the tool code will remain>",
        py_modules=["my_tool", "app"],
        packages=find_packages(),
        install_requires=[requirements],
        python_requires=">=3.7",
        classifiers=[
            "Programming Language :: Python :: 3.1ß",
            "Operating System :: OS Independent",
        ],
    )
