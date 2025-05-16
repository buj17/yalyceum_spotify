# import time
# from concurrent.futures import ThreadPoolExecutor
#
# import db.s3manager
# from db.s3manager import S3Manager
#
#
# def get_url_pair(music_id: int):
#     with S3Manager() as s3_manager:
#         return (s3_manager.get_file_url(f'music_audio_{music_id}.mp4',
#                                         content_type='audio/mp3',
#                                         content_disposition='inline'),
#                 s3_manager.get_file_url(f'music_image_{music_id}.jpg',
#                                         content_type='image/jpeg',
#                                         content_disposition='inline'))
#
#
# if __name__ == '__main__':
#     t = time.perf_counter()
#     print(t)
#     # for i in range(100, 125):
#     #     print(get_url_pair(s3_manager, i))
#     with ThreadPoolExecutor(max_workers=100) as executor:
#         urls = list(executor.map(get_url_pair, range(100, 200)))
#     print(urls)
#     print(time.perf_counter() - t)
import pprint
import time

from db import create_session
from db.managers import MusicManager

keys = range(100, 175)

if __name__ == '__main__':
    t = time.perf_counter()
    print(t)

    db_session = create_session()
    urls = MusicManager(db_session).get_music_url_pairs(*range(100, 200))
    db_session.close()

    pprint.pprint(urls)
    print(time.perf_counter() - t)
