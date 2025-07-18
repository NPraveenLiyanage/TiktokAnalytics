from TikTokApi import TikTokApi as tiktok
import json  #Import json for export data

# #Get cookie data
verifyFp = "s_Xv__t4BOVZVUCye44Pi8YnhZaOTeiCWNktNOpfL3fsIl9kBb6Bg1qy2FXus4WnRAcSTTw6nokhQrUOzEeV5fWPuMopThBF_7cksvg81NpM3KKiSksx3nejlSMRrbNYBfTPl8kffYFcyo1LREMBfrLs"
# #Setup instance
# api = tiktok.get_instance(custome_verifyFp = verifyFp, use_test_endpoints = True)
# #Get data by hashtag
# trending = api.by_hashtag('python')
# print(trending)

import os
from TikTokApi import TikTokApi
import asyncio

# Set your ms_token manually
ms_token = "s_Xv__t4BOVZVUCye44Pi8YnhZaOTeiCWNktNOpfL3fsIl9kBb6Bg1qy2FXus4WnRAcSTTw6nokhQrUOzEeV5fWPuMopThBF_7cksvg81NpM3KKiSksx3nejlSMRrbNYBfTPl8kffYFcyo1LREMBfrLs"

async def fetch_by_hashtag():
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=3,
            browser="chromium"
        )

        videos_data = []
        async for video in api.trending.videos(count=5):
            print(video.as_dict)  # Debug print
            videos_data.append(video.as_dict)

        # ✅ Write to export.json as valid JSON
        with open('export.json', 'w', encoding='utf-8') as f:
            json.dump(videos_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    asyncio.run(fetch_by_hashtag())

