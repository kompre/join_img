from setuptools import setup

setup(
    package='find',
    name='join_img_html',
    version='0.1',
    py_modules=['cli_join_img_from_html'],
    install_requires=[
        'click==8.0.0',
        'ordered-set==4.0.2',
        'Pillow==8.2.0'
    ],
    entry_points='''
        [console_scripts]
        join_img_html=cli_join_img_from_html:join_img_html
    ''',
)