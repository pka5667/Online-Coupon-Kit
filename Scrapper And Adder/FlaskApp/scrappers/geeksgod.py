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
    except Exception as e:
        error_type, error_obj, error_info = sys.exc_info() 
        print ('ERROR FOR LINK:', url)
        print (error_type, 'Line:', error_info.tb_lineno)
        return 
        

    # GET ALL THE COURSES GEEKSGOD DETAIL PAGE LINK
    soup = BeautifulSoup(page.text, "html.parser")
    allCourses = soup.find_all("div", attrs={'class': 'td-block-span6'})

    print("1/4")
    # OPEN EACH COUPON LINK AND GET COUPON CODE FOR EVERY 
    geeksgod_couse_detail_page_url = []
    for block in allCourses:
        try:
            link = block.find('h3').find('a')['href']
            geeksgod_couse_detail_page_url.append(link)
        except Exception as e:
            print(e, 'GeeksGod Home Page')



    # GO TO DETAIL PAGE NOW
    print("2/4")
    geeksgod_link_page_url = []
    for detail_page_url in geeksgod_couse_detail_page_url:
        try:
            r = requests.get(detail_page_url)
            soup = BeautifulSoup(r.text, "html.parser")
            html = soup.findAll('div', attrs={'class': 'elementor-row'})[1]
            html.findAll('div', attrs={'class': 'elementor-column'})[1]
            # find coupon code and next page url to generate udemy course link url
            coupon_code = soup.find('div', attrs={'class': 'elementor-element-95b43f4'}).find('p', attrs={'class': 'elementor-heading-title'}).get_text()
            link_page_url = soup.find('div', attrs={'class': 'elementor-element-abf6e0b'}).find('a', attrs={'class': 'elementor-button-link'})['href']
            geeksgod_link_page_url.append({'coupon_code': coupon_code, 'geeksgod_link_page': link_page_url})
        except Exception as e:
            print(e, 'GeeksGod Detail Page', detail_page_url)



    # NOW GET THE LINK OF COUSE ON UDEMY OFFICIAL WEBSITE from all the geeksgod_link_page_urls
    print("3/4")
    udemy_course_urls = []
    for i in geeksgod_link_page_url:
        try:
            r = requests.get(i['geeksgod_link_page'])
            soup = BeautifulSoup(r.text, "html.parser")
            link = soup.findAll('div', attrs={'class': 'elementor-button-wrapper'})[2].find('a')['href']
            link = link.split('murl=')[1]
            link = link.replace('%3A', ':').replace('%2F', '/')
            coupon_code = i['coupon_code']
            udemy_course_urls.append({'coupon_code': coupon_code, 'udemy_course_link': link})
        except Exception as e:
            print(e, "Udemy Course link page on GeeksGod", i['geeksgod_link_page'])



    # OPEN THE UDEMY LINK AND GET ALL THE REQUIRED DATA 
    coupon_details = []
    print("4/4")
    for i in udemy_course_urls:
        try:
            url = i['udemy_course_link'].replace('%3F', '')
            coupon_code = i['coupon_code']
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            # title = soup.find('h1', attrs={'data-purpose': 'lead-title'}).get_text()
            # thumbnail_url = soup.find('span', attrs={'class': 'intro-asset--img-aspect--1UbeZ'}).find('img')['src']
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


# save image to media folder from url 
def save_image(img_url):
    name = img_url.split('/')[-1]
    file_path = f'media/udemy/{name}'
    if not os.path.exists(file_path):
        f = open(file_path, 'wb')
        f.write(requests.get(img_url).content)
        f.close()
    return 'udemy/' + name



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
def fetch_geeksgod_links(start=1, end=3):
    coupon_details = []
    for i in range(start, end+1):
        print("Fetching", f'https://geeksgod.com/category/freecoupons/udemy-courses-free/page/{i}')
        coupon_details = coupon_details + fetch_all_udemy_coupon_codes(f'https://geeksgod.com/category/freecoupons/udemy-courses-free/page/{i}')
    return coupon_details


# MAIN FUNCTION 
if __name__ == '__main__':
    print(fetch_geeksgod_links(1, 3))
