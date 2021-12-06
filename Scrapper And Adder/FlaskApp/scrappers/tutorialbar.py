import requests
import sys
from bs4 import BeautifulSoup
import os
import cloudinary
from cloudinary.uploader import upload as cloudinary_upload
from cloudinary.utils import cloudinary_url




def fetch_all_udemy_coupon_codes(url):
    # FETCH THE MAIN PAGE OF WEBSITE
    try:
        page = requests.get(url)
    except Exception:
        error_type, error_obj, error_info = sys.exc_info() 
        print ('ERROR FOR LINK:', url)
        print (error_type, 'Line:', error_info.tb_lineno)
        return []
        
    print("1/3")
    # GET ALL THE COURSES GEEKSGOD DETAIL PAGE LINK
    soup = BeautifulSoup(page.text, "html.parser")
    allCourses = soup.find_all("article")
    for i in range(len(allCourses)):
        allCourses[i] = allCourses[i].find("div", attrs={'class': 'content_constructor'})


    # OPEN EACH COUPON LINK AND GET COUPON CODE FOR EVERY 
    tutorialbar_couse_detail_page_url = []
    for block in allCourses:
        try:
            link = block.find('h3').find('a')['href']
            tutorialbar_couse_detail_page_url.append(link)
        except Exception as e:
            print(e, 'Tutorialbar Home Page')


    print("2/3")
    # NOW GET THE LINK OF COUSE ON UDEMY OFFICIAL WEBSITE from all the geeksgod_link_page_urls
    udemy_course_urls = []
    for i in tutorialbar_couse_detail_page_url:
        try:
            r = requests.get(i)
            soup = BeautifulSoup(r.text, "html.parser")
            link = soup.find("div", attrs={'class': 'priced_block'}).find('a')['href']
            link_split = link.split('?couponCode=')
            link = link_split[0]
            coupon_code = link_split[1]
            udemy_course_urls.append({'coupon_code': coupon_code, 'udemy_course_link': link})
        except Exception as e:
            print(e, "Udemy Course link page on tutorialbar", i)


    print("3/3")
    # OPEN THE UDEMY LINK AND GET ALL THE REQUIRED DATA 
    coupon_details = []
    for i in udemy_course_urls:
        try:
            url = i['udemy_course_link'].replace('%3F', '')
            coupon_code = i['coupon_code']
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find('meta', attrs={'property': 'og:title'})['content']
            description = soup.find('meta', attrs={'property': 'og:description'})['content']
            what_you_will_learn = ""
            for ul in soup.select('ul[class*="what-you-will-learn--objectives-list"]'):
                li = ul.findAll('li')
                for num in range(len(li)):
                    what_you_will_learn = f'{what_you_will_learn}\n{num+1}. {li[num].get_text()}'
            thumbnail_url   = soup.find('meta', attrs={'property': 'og:image'})['content']
            thumbnail_url   = upload_to_cloudinary(thumbnail_url)
            category        = soup.find('meta', attrs={'property': 'udemy_com:category'})['content']
            original_price  = soup.find('meta', attrs={'property': 'udemy_com:price'})['content']
            coupon_details.append({'title': title, 
                                    'description': description, 
                                    'thumbnail_url': thumbnail_url, 
                                    'category': category,
                                    'what_you_will_learn': what_you_will_learn,
                                    'original_price': original_price,  # will decide later if its in usd or inr according to django's time zone
                                    'coupon_code': coupon_code,
                                    'course_url': url
                                    })
        except Exception as e:
            print(e, "Udemy Course Official Page", i['udemy_course_link'])

    return coupon_details



# Upload files to cloudinary
def upload_to_cloudinary(img_url):
    cloudinary.config(cloud_name = "drq1m87mu", api_key = "962834934286717", api_secret = "KA-BQ_JW-3Od47z1wxUJFQ1HmaM",secure = True)
    
    while img_url[-1] == '/': img_url = img_url[:-1]
    name = img_url.split('/')[-1].split('.')[0]
    response = cloudinary_upload(img_url, tags = 'Udemy Course', public_id = f'Online-Coupon-Kit/Udemy-Course/{name}')
    
    url, options = cloudinary_url(
        response['public_id'],
        format=response['format'],
    )
    url.replace('.jpg', '.AVIF')
    return url
    


# FUNCTION TO CALL ALL FATCHES
def fetch_tutorialbar_links():
    coupon_details = []
    print("Fetching", 'https://www.tutorialbar.com/')
    coupon_details = coupon_details + fetch_all_udemy_coupon_codes('https://www.tutorialbar.com/')
    return coupon_details


# MAIN FUNCTION 
if __name__ == '__main__':
    print(fetch_tutorialbar_links())
