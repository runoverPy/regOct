from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
desc = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="regOct",
    version='1.1.0',
    description="A module implementing octrees for python",
    long_description=desc,
    long_description_content_type='text/markdown',
    url='https://github.com/runoverPy/regOct',
    author="runover",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(where="src"),
    package_dir = {"":"src"},
    python_requires=">=3, <4",
    install_requires=[
        "PyGLM",
        "numpy",
        "keyboard",
        "glfw",
        "PyOpenGL",
        "tqdm",
    ],
)