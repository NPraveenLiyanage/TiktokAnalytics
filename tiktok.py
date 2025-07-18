from TikTokApi import TikTokApi as tiktok
import json  #Import json for export data
#import data processing helper
from helpers import process_result
import pandas as pd
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
        async for video in api.trending.videos(count=30):
            print(video.as_dict)  # Debug print
            videos_data.append(video.as_dict)

        flatten_data = process_result(videos_data)

        # # ✅ Write to export.json as valid JSON
        # with open('export.json', 'w', encoding='utf-8') as f:
        #     json.dump(flatten_data, f, ensure_ascii=False, indent=4)

        #conver the preprocessed data to a dataframe
        if flatten_data:
            print("Data processed. Writing to CSV...")
            try:
                df = pd.DataFrame.from_dict(flatten_data, orient='index')
                df.to_csv('tiktokdata.csv', index=False)
                print("CSV exported: tiktokdata.csv")
            except Exception as e:
                print("❌ Error writing CSV:", e)
        else:
            print("⚠️ No data to export. flatten_data is empty.")

        print("Current working dir:", os.getcwd())



if __name__ == "__main__":
    asyncio.run(fetch_by_hashtag())


