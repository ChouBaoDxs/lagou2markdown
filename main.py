import logging
import os
import re
import traceback
from urllib.request import urlretrieve
import yaml

import html2text
import requests

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)7s: %(message)s')
logger = logging.getLogger(__name__)


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def clear_slash(s: str) -> str:
    return s.replace('\\', '').replace('/', '').replace('|', '')


img_pattern = re.compile(r'(http.*?(?:jpg|png|JPG|PNG))')


class LagouBook2Markdown:
    def __init__(self, config: dict):
        logger.info(config)
        pwd = os.path.dirname(os.path.abspath(__file__))
        default_save_dir = os.path.join(pwd, 'book')
        gate_login_token: str = config['gate_login_token']
        self.course_ids: list = config['course_ids']
        self.save_dir: str = config.get('save_dir', default_save_dir)
        self.request_headers = {
            'cookie': f'gate_login_token={gate_login_token};',
            'x-l-req-header': '{deviceType:1}',
        }
        makedirs(self.save_dir)

    def get_course_lessons_res(self, course_id) -> requests.Response:
        url = f'https://gate.lagou.com/v1/neirong/kaiwu/getCourseLessons?courseId={course_id}'
        res = requests.get(url, headers=self.request_headers)
        # logger.info(res.text)
        return res

    def get_lesson_res(self, lesson_id) -> requests.Response:
        url = f'https://gate.lagou.com/v1/neirong/kaiwu/getCourseLessonDetail?lessonId={lesson_id}'
        res = requests.get(url, headers=self.request_headers)
        # logger.info(res.text)
        return res

    @classmethod
    def save_markdown(cls, md_file_path, img_dir, md_relative_img_dir, markdown_html_str):
        markdown_str = html2text.html2text(markdown_html_str)
        img_urls = re.findall(img_pattern, markdown_str)
        for img_index, img_url in enumerate(img_urls):
            suffix = os.path.splitext(img_url)[-1]
            img_file_name = f'{img_index + 1}{suffix}'
            md_relative_img_path = os.path.join(md_relative_img_dir, img_file_name)
            img_save_path = os.path.join(img_dir, img_file_name)
            urlretrieve(img_url, img_save_path)
            markdown_str = markdown_str.replace(img_url, md_relative_img_path)
        with open(md_file_path, 'w', encoding='utf8') as f:
            f.write(markdown_str)

    def deal_a_course(self, course_id):
        log_data = {
            'course_id': course_id,
            'msg': '开始处理课程'
        }
        logger.info(log_data)

        # 获取课程名和 lesson_id 列表
        res = self.get_course_lessons_res(course_id)
        res_json = res.json()
        course_section_list = res_json['content']['courseSectionList']
        course_name: str = res_json['content']['courseName']
        course_name = clear_slash(course_name)
        course_save_path = os.path.join(self.save_dir, course_name)
        img_dir = os.path.join(course_save_path, 'img')
        makedirs(img_dir)

        lesson_id_list = []
        for section in course_section_list:
            section_lesson_list = section['courseLessons']
            lesson_id_list.extend([_['id'] for _ in section_lesson_list])

        lesson_count = len(lesson_id_list)
        for index, lesson_id in enumerate(lesson_id_list):
            lesson_order = index + 1
            logger.info({
                '进度': f'{lesson_order}/{lesson_count}',
                'msg': '处理 lesson',
                'lesson_id': lesson_id
            })
            res = self.get_lesson_res(lesson_id)
            res_json = res.json()
            lesson_title = res_json['content']['theme']
            lesson_title = clear_slash(lesson_title)
            text_content_html = res_json['content']['textContent']
            lesson_md_file_path = os.path.join(course_save_path, f'{lesson_order}-{lesson_title}.md')
            lesson_img_dir = os.path.join(img_dir, f'{lesson_order}')
            makedirs(lesson_img_dir)
            md_relative_img_dir = os.path.join('img', f'{lesson_order}')
            self.save_markdown(lesson_md_file_path, lesson_img_dir, md_relative_img_dir, text_content_html)
        log_data['msg'] = '处理完成'
        logger.info(log_data)

    def main(self):
        for course_id in self.course_ids:
            try:
                self.deal_a_course(course_id)
            except Exception as e:
                log_data = {
                    'course_id': course_id,
                    'e': repr(e),
                    'traceback': traceback.format_exc(),
                    'msg': '处理课程出错'
                }
                logger.error(log_data)


if __name__ == '__main__':
    with open('config.yml', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    helper = LagouBook2Markdown(config)
    helper.main()
