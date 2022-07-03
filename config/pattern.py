# _*_ coding: utf-8 _*_
"""
Time:     2022/7/1 16:57
Author:   不做评论(vvbbnn00)
Version:  
File:     pattern.py
Describe: 正则表达式
"""

USER_PATTERN = r"^[a-zA-Z0-9]{3,15}$"
PASSWD_PATTERN = r"^(?=.*\d)(?=.*[a-zA-Z]).{8,20}$"
COURSE_ID_PATTERN = r"^[a-zA-z0-9-]{5,30}$"
COURSE_TITLE_PATTERN = r"^[a-zA-Z0-9()（）\u4e00-\u9fa5-]{5,50}$"
COURSE_DESCRIPTION_PATTERN = r"^[\D0-9]{5,250}$"
COURSE_TYPE_PATTERN = r"^[0-3]{1}$"
SEMESTER_PATTERN = r"^[a-zA-Z0-9-]{4,10}$"
NUMBER_PATTERN = r"^[+]{0,1}(\+)$"
POINTS_PATTERN = r"^[+]{0,1}(\d+)$|^[+]{0,1}(\d+\.\d{1,2})$"
USER_NAME_PATTERN = r"^[ 0-9a-zA-Z\u4e00-\u9fa5·]{2,20}$"
SCHOOL_NAME_PATTERN = r"^[a-zA-Z0-9()（）\u4e00-\u9fa5- ]{3,50}$"
