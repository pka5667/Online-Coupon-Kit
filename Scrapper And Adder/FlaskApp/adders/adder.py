'''
Add all scrapped courses to database and schedule to telegram channel
1. Call the scrapper functions 
2. Connect to database
3. Check the courses in database and add new courses
4. Send a message to telegram bot to schedule it 
'''
'''
Add all scrapped courses to database and schedule to telegram channel
1. Call the scrapper functions 
2. Add new courses - using post request api
3. Send a message to telegram bot to schedule it 
'''

from scrappers.geeksgod import fetch_geeksgod_links
from scrappers.tutorialbar import fetch_tutorialbar_links
import requests
import json
import os
from time import sleep

# fetch from page start to page end
def add_to_database():
  try:
    added_courses_urls = []
    URL = os.environ['ADDER_URL']
    # SCRAPPERS CALLIN#G 
    courses = []
    courses = courses + fetch_geeksgod_links()
    print(f'Got total {len(courses)} courses')
    sleep(60)
    courses = courses + fetch_tutorialbar_links()
    print(f'Got total {len(courses)} courses')

    # CREATING NEW DATA IN COURSE COLLECTION - By making post request
    for course in courses:
      try:
        data = {
            'password': os.environ['DATABASE_POST_PASSWORD'],
            'title': course['title'],
            'description': course['description'],
            'thumbnail_url': course['thumbnail_url'],
            'category': course['category'],
            'what_you_will_learn': course['what_you_will_learn'],
            'original_price': course['original_price'],
            'coupon_code': course['coupon_code'],
            'course_url': course['course_url'],
        }
        #send post request
        r = requests.post(URL, data=data)
        try:
          r = json.loads(r.text)
        except Exception as e:
          print(course['course_url'], e)
          continue

        # if r['type'] == 'course added successfully':
        #     response = f"-----\n\n*{r['title']}*\n\n{r['description']}\n\nPrice: ~~{r['original_price']}~~ *FREE*\n\nUse Coupon: *{r['coupon_code']}*\n\nLink: {r['final_course_url']}\n"
        #     added_courses_urls.append(response)

        if r['type'] == 'course added successfully':
            response = {
                'thumbnail_url': r['thumbnail_url'],
                'message': f"*{r['title']}*\n\n{r['final_course_url']}"
            }
            added_courses_urls.append(response)
      except Exception as e:
        print(course['course_url'], e)

    return added_courses_urls
  except Exception as e:
    print("Adder file", e)

