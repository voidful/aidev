from setuptools import setup, find_packages

setup(
    name="aitester",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "click",
        "gitpython",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "aitester=aitester:main",
            'aitester-config=aitester.config_manager:manage_config'
        ],
    },
)
