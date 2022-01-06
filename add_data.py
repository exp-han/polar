import requests
import pgeocode as pg

from pymongo import MongoClient
from requests import api

client = MongoClient('localhost', 27017)
db = client.polar

# TODO:
# API_KEY 마스킹 할 것
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

# TODO:
# 클라이언트에서 radius 받아 올 것 
# zipcode는 아직 안쓸지도 모르는데, zipcode 기반 좌표함수에 넣어서 좌표 얻어낼 것
# Default radius = 5 miles (8046.72 m)
def insert_hospital(l, r=8046.72):
    location, radius = l, r    
    hospital_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?inputtype=textquery&type=veterinary_care&key={api_key}&radius={radius}&location={location}".format(api_key=api_key, radius=radius, location=location)
    data = requests.get(hospital_url, headers=headers).json()
    hospitals = data["results"]
    for h in hospitals:
        name = h["name"]
        business_status = h["business_status"]
        address = h["formatted_address"]
        geometry = h["geometry"]["location"]
        gplace_id = h["place_id"]
        rating = h["rating"]
        hos = db.hospital.find_one({'gplace_id': gplace_id}, {'_id':0})
        doc = {
            'name': name,
            'business_status': business_status,
            'address': address, 
            'geometry': geometry,
            'gplace_id': gplace_id,
            'rating': rating
        }
        db.hospital.insert_one(doc)
        print('HOSPITAL INSERTION COMPLETE:', name)

# TODO:
# 상세정보용 디테일 insertion
# update part 수정할 것
def insert_details_hospital(gplace_id):
    hos = db.hospital.find_one({'gplace_id': gplace_id}, {'_id':0})
    detail_url = "https://maps.googleapis.com/maps/api/place/details/json?key={api_key}&place_id={placeid}".format(api_key=api_key, placeid=gplace_id)
    data = requests.get(detail_url, headers=headers)
    details = data['result']

    phone = details['formatted_phone_number']
    # reviews = array type
    reviews = details['reviews']
    db.hospital.update_one({'gplace_id': gplace_id},{'$set':{'phone':phone}})
    db.hospital.update_one({'gplace_id': gplace_id},{'$set':{'reviews':reviews}})

# TODO:
# 클라이언트에서 zipcode / loc , r 받아오기
# Default radius = 5 miles (8046.72 m)
def insert_shelter(l, r=8046.72):
    location, radius = l, r
    shelter_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?sensor=false&keyword='pet%20shelter'&key={api_key}&location={location}&radius={radius}".format(api_key=api_key, location=location, radius=radius)
    data = requests.get(shelter_url,headers=headers).json()
    shelters = data["results"]
    for s in shelters:
        name = s["name"]
        business_status = s["business_status"]
        address = s["formatted_address"]
        geometry = s["geometry"]["location"]
        gplace_id = s["place_id"]
        rating = s["rating"]
        doc = {
            'name': name,
            'business_status': business_status,
            'address': address, 
            'geometry': geometry,
            'gplace_id': gplace_id,
            'rating': rating
        }
        db.shelter.insert_one(doc)
        print('SHELTER INSERTION COMPLETE: ', name)

# TODO: 
# use petfinder API
def insert_tmppro(url):
    return

# TODO:
# 클라이언트에서 zipcode 받아온 후 -> db에 없으면 calcloc 하고 db에 넣기
# 있으면 db에서 긁어오기
# calculate_loc(zipcode, country)
# used in insert_zipcode_loc(z, c)
# param: z = client input zipcode, c = client input country
# return: string of "latitude, longitude", used as input for google places API
def calculate_loc(z, c):
    nomi = pg.Nominatim(c)
    res = nomi.query_postal_code(z)
    latitude = res["latitude"]
    longitude = res["longitude"]
    return "{lat}, {long}".format(lat=latitude, long=longitude)

# insert_zipcode_loc(z, c)
# param: z = client input zipcode, c = client input country
# return: None
def insert_zipcode_loc(z, c='us'):
    zipcode, country = z, c
    latlongstr = calculate_loc(z, country)
    doc = {
        'zipcode': zipcode,
        'latlong': latlongstr
    }
    db.ziplatlong.insert_one(doc)
    print('ZIPCODE INSERTION CCMOPLETE: country: {c} zipcode: {z} latlong: {l}'.format(c=country, z=zipcode, l=latlongstr))
    return latlongstr

### Testing
# if __name__=="__main__":
#     print(calculate_loc(544))

# 할 일:
# 1. init_db.py
# 구글 places API에서 동물병원, 쉘터 리스트 받아온 후 name addr zipcode business_status 받아오기
# 가능하다면 google 리뷰도 받아올 것
# 2. 메인페이지 만들기
# 메인 검색창에서 우편번호 검색 후 -> 거리순 정렬로 (가까운 순으로) 병원, 쉘터 가져올 것 + 거리 출력 할 것
# 3. 검색 결과 페이지 만들기 (대부분 UI 디자인)
# 2번의 결과값 리스트를 가져와서 출력해주기
# 4. 검색 필터 넣어주기 + 임시보호 동물 API 가져올 것
# 5. 시설 상세페이지 가져오기 + 리뷰 가져오기
# 구글 리뷰 가능하면 가져올 것
# 리뷰 상세페이지 디자인
# 6. 로그인 기능 만들기 + 리뷰 작성 UI + No review UI

# 만들 페이지:
# 1. 메인 페이지
# 2. 로그인 페이지
# 3. 검색결과 페이지
# 4. 상세 페이지 (리뷰 페이지)
