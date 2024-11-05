# Copyright 2024. ZiTTA All rights reserved.
# Youtube-playlist_API
# 2024-10-04

import requests
from datetime import datetime, timedelta
import json

# API 키와 재생목록 ID 설정
playlist_url = r"Playlist_URL"  # r(읽기 모드)로 실행.
api_key = "YOUR_API_KEY"
playlist_id = playlist_url.split('=')[1]

# 한 번에 가져올 수 있는 최대 결과 수
max_results = 50

# API 요청 URL 설정
url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults={max_results}&key={api_key}"

# pageToken을 통해 여러 페이지 불러오기
def fetch_playlist_items(api_url):
    next_page_token = None
    all_items = []

    while True:
        # pageToken이 있는 경우 URL에 추가
        if next_page_token:
            url = f"{api_url}&pageToken={next_page_token}"
        else:
            url = api_url

        # API 호출
        response = requests.get(url)
        data = response.json()

        # 현재 페이지의 항목 추가
        all_items.extend(data["items"])

        # 다음 페이지가 있는지 확인
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return all_items

# 모든 재생목록 항목 불러오기
items = fetch_playlist_items(url)

# 시간 형식을 변환한 후 원본 데이터에 KST 시간 추가
for idx, item in enumerate(items, start=1):
    # title, publishedAt, videoOwnerChannelTitle 필드명 변경
    item["snippet"]["제목"] = item["snippet"].pop("title")
    item["snippet"]["추가한 날짜"] = item["snippet"].pop("publishedAt")
    # item["snippet"]["채널 이름"] = item["snippet"].pop("videoOwnerChannelTitle")

    # 시간 문자열을 datetime 객체로 변환 (UTC 시간대)
    iso_time = item["snippet"]["추가한 날짜"]
    parsed_time = datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%SZ")

    # UTC 시간을 UTC+9로 변환 (한국 표준시)
    kst_time = parsed_time + timedelta(hours=9)

    # 원하는 형식으로 시간 변환
    formatted_time = kst_time.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")

    # 번호를 추가하여 데이터에 추가
    item["snippet"]["번호"] = idx

    # '추가한 날짜' 필드에 변환된 시간 덮어쓰기
    item["snippet"]["추가한 날짜"] = formatted_time

    # snippet 밖에서 삭제할 필드 목록 (필요 시 추가)
    fields_to_delete_outside_snippet = ["kind", "etag", "id"]  # 여기에 삭제할 필드명을 추가
    
    # snippet 안의 삭제할 필드 목록 (필요 시 추가)
    fields_to_delete_in_snippet = ["channelId", "description", "thumbnails", "channelTitle", "playlistId", "resourceId", "position", "videoOwnerChannelId"]  # 여기에 삭제할 필드명을 추가
    
    # 반복문으로 여러 필드를 삭제
    for field in fields_to_delete_in_snippet:  # snippet 안의 필드를 삭제
        item["snippet"].pop(field, None)  # None을 넣으면 해당 키가 없어도 에러가 나지 않음
    for field in fields_to_delete_outside_snippet:  # snippet 밖의 필드를 삭제
        item.pop(field, None)  # None을 넣으면 해당 키가 없어도 에러가 나지 않음

# JSON 파일로 저장 (원본 데이터를 유지하면서 KST 시간 추가)
with open('playlist_data.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=4)

print("데이터가 'playlist_data.json' 파일에 저장되었습니다.")
