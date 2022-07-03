import json

import exceptions.course_exceptions
from mysql import pool

QUERY_ORDER_BY = {
    0: "course_id ASC",
    1: "points DESC",
    2: "points ASC"
}

WEEKDAY_DICT = " 一二三四五六日"

if __name__ == '__main__':
    search_kw = None
    semester = "2022-1"
    page = 10
    page_size = 10
    pool.getconn()

    course_data = {
        'week_start': 1,
        'week_end': 16,
        'schedule': {"1": [], "2": [10, 11, 12], "3": [], "4": [], "5": [], "6": [], "7": []}
    }

    ret = pool.getAll(f"""select courses.schedule as schedule, 
    courses.title as title, courses.course_id as course_id from selections,courses 
    where selections.uid=%s and courses.semester=%s and courses.course_id=selections.course_id and
    ((courses.week_start>=%s and courses.week_start<=%s)or(courses.week_end>=%s and courses.week_end<=%s));""",
                      ["2135060620", "2022-1", course_data['week_start'], course_data['week_end'],
                       course_data['week_start'], course_data['week_end']])
    if not ret:
        ret = []

    for course in ret:
        schedule = json.loads(course['schedule'])
        for key, value in schedule.items():
            course_schedule = set(course_data['schedule'][key])
            selected_course_schedule = set(value)
            conflicted_schedule = [str(item) for item in course_schedule & selected_course_schedule]

            if len(conflicted_schedule) > 0:
                raise exceptions.course_exceptions.CourseSelectFailed(
                    f"您选的课程与课程\"{course['title'].decode()}\"在周{WEEKDAY_DICT[int(key)]}的第{','.join(conflicted_schedule)}节课有冲突")

    print(ret)
