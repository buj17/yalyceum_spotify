from io import BytesIO

import boto3
from botocore.response import StreamingBody
from types_boto3_s3 import S3Client
from types_boto3_s3.service_resource import BucketObjectsCollection

BUCKET_NAME = 'melodia'


class S3Manager:
    """
    Класс для управления файлами в s3 хранилище
    """

    def __init__(self):
        self._session = boto3.session.Session()
        self._s3_client: S3Client = self._session.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net'
        )

    def get_file(self, filename: str) -> StreamingBody:
        """Получение файла из s3 хранилища

        :param filename: Название файла, которое необходимо загрузить
        :type filename: str
        :raises ValueError: Если файл с таким именем не существует
        :return: StreamingBody объект для работы с файлом
        :rtype: StreamingBody
        """
        try:
            file_object = self._s3_client.get_object(
                Bucket=BUCKET_NAME,
                Key=filename
            )['Body']
        except Exception as ex:
            raise ValueError(f'File not found: {filename}') from ex

        return file_object

    def upload_file(self, filename: str, content: BytesIO | StreamingBody, force: bool = False) -> None:
        """Загрузка файла в s3 хранилище

        :param filename: Название, под которым требуется сохранить файл
        :type filename: str
        :param content: BytesIO или StreamingBody объект с содержимым файла
        :type content: BytesIO | StreamingBody
        :param force: Игнорировать существование файла
        :type force: bool
        :raises ValueError: Если файл с таким именем уже существует
        """
        if not force and self._file_exists(filename):
            raise ValueError(f'File already exists: {filename}')

        self._s3_client.upload_fileobj(
            Fileobj=content,
            Bucket=BUCKET_NAME,
            Key=filename
        )

    def delete_file(self, filename: str) -> None:
        """Удаление файла из s3 хранилища

        :param filename: Название файла, который требуется удалить
        :type filename: str
        :raises ValueError: Если файл с таким именем не существует
        """
        if not self._file_exists(filename):
            raise ValueError(f'File not found: {filename}')

        self._s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=filename
        )

    def update_file(self, filename: str, content: BytesIO | StreamingBody) -> None:
        """Обновление данных файла в s3 хранилище

        :param filename: Название файла, который требуется обновить
        :type filename: str
        :param content: BytesIO или StreamingBody объект с новым содержимым файла
        :type content: BytesIO | StreamingBody
        :raises ValueError: Если файл с таким именем уже существует
        """
        if not self._file_exists(filename):
            raise ValueError(f'File not found: {filename}')

        self._s3_client.upload_fileobj(
            Fileobj=content,
            Bucket=BUCKET_NAME,
            Key=filename
        )

    def get_objects_collection(self) -> BucketObjectsCollection:
        """Возвращает объект для просмотра информации о всех файлах в хранилище

        :return: BucketObjectsCollection объект
        :rtype: BucketObjectsCollection
        """
        s3_resource = self._session.resource('s3')
        s3_bucket = s3_resource.Bucket(name=BUCKET_NAME)
        bucket_objects_collection = s3_bucket.objects.all()
        return bucket_objects_collection

    def get_file_url(self):
        pass

    def _file_exists(self, filename: str):
        try:
            self.get_file(filename)
        except ValueError:
            return False
        return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._s3_client.close()


# if __name__ == '__main__':
#     s3_manager = S3Manager()
#     file_name = "Love Today (Telugu) (Original Motion Picture Soundtrack).mp3"
#     file_path = r"C:\Users\KUSLY\PycharmProjects\WorkDirectory\music_project\yalyceum_spotify\api\media\Love Today (Telugu) (Original Motion Picture Soundtrack).mp3"
#     # Чтение файла и создание BytesIO
#     with open(file_path, 'rb') as file:
#         mp3_bytes = file.read()
#         mp3_bytes_io = BytesIO(mp3_bytes)
#
#     # Загрузка файла в S3
#     s3_manager.upload_file(file_name, mp3_bytes_io)


# if __name__ == '__main__':
#     s3_manager = S3Manager()
#     file_name = "Love Today (Telugu) (Original Motion Picture Soundtrack).mp3"
#     # Получаем файл из S3
#     streaming_body = s3_manager.get_file(file_name)
#
#     # Указываем путь для сохранения локально
#     local_file_path = "downloaded_" + file_name
#
#     # Сохраняем содержимое в файл
#     with open(local_file_path, 'wb') as f:
#         f.write(streaming_body.read())
#
#     print(f"Файл успешно сохранён как {local_file_path}")