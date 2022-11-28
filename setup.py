from setuptools import setup

setup(
    package='find',
    name='join_img_html',
    version='0.3',
    py_modules=['cli_join_img_from_html'],
    install_requires=[
        'click==8.1.3',
        'Pillow'
        # 'Pillow==8.2.0'
    ],
    entry_points='''
        [console_scripts]
        join_img_html=cli_join_img_from_html:join_img_html
    ''',
)