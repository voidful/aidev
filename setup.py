from setuptools import setup, find_packages

setup(
    name="aidev",
    version="0.4",
    packages=find_packages(),
    install_requires=[
        "click",
        "gitpython",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "aidev=aidev:main",
            'aidev-config=aidev.config_manager:manage_config'
        ],
    },
)
