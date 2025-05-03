from io import BytesIO

import boto3
from botocore.response import StreamingBody
from types_boto3_s3 import S3Client

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
        :raises ValueError: Если данный не найден в хранилище
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

    def upload_file(self, filename: str, content: BytesIO | StreamingBody) -> None:
        """Загрузка файла в s3 хранилище

        :param filename: Название, под которым требуется сохранить файл
        :type filename: str
        :param content: BytesIO или StreamingBody объект с содержимым файла
        :type content: BytesIO | StreamingBody
        :raises ValueError: Если файл с таким именем уже существует
        """
        if self._file_exists(filename):
            raise ValueError('File already exists: {}'.format(filename))

        self._s3_client.upload_fileobj(
            Fileobj=content,
            Bucket=BUCKET_NAME,
            Key=filename
        )

    def delete_file(self, filename: str) -> None:
        """Удаление файла из s3 хранилища

        :param filename: Название файла, который требуется удалить
        :type filename: str
        :raises ValueError: Если файла с таким именем не существует
        """
        if not self._file_exists(filename):
            raise ValueError('File not found: {}'.format(filename))

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
            raise ValueError('File not found: {}'.format(filename))

        self._s3_client.upload_fileobj(
            Fileobj=content,
            Bucket=BUCKET_NAME,
            Key=filename
        )

    def _file_exists(self, filename: str):
        try:
            self.get_file(filename)
        except ValueError:
            return False
        return True
