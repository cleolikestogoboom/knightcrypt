from setuptools import setup, find_packages

setup(
    name="knighted",
    version="4.0.0",
    author="Sancho",
    description="cool python encryption lib yesyes",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pycryptodome",
        "psutil",
    ],
    entry_points={
        'console_scripts': [
            'knightcrypt=knightcrypt.knightcrypt:main',
        ],
    },
)
