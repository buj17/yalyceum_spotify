from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from typing import Any, Sequence

import boto3
from botocore.response import StreamingBody
from types_boto3_s3 import S3Client
from types_boto3_s3.service_resource import BucketObjectsCollection

BUCKET_NAME = "melodia"


class S3Manager:
    """
    Класс для управления файлами в s3 хранилище
    """

    def __init__(self):
        self._session = boto3.session.Session()
        self._s3_client: S3Client = self._session.client(
            service_name="s3",
            endpoint_url="https://storage.yandexcloud.net"
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
            )["Body"]
        except Exception as ex:
            raise ValueError(f"File not found: {filename}") from ex

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
            raise ValueError(f"File already exists: {filename}")

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
            raise ValueError(f"File not found: {filename}")

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
            raise ValueError(f"File not found: {filename}")

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
        s3_resource = self._session.resource("s3")
        s3_bucket = s3_resource.Bucket(name=BUCKET_NAME)
        bucket_objects_collection = s3_bucket.objects.all()
        return bucket_objects_collection

    def get_file_url_safe(self, filename: str,
                          content_type: str,
                          content_disposition: str,
                          default: Any = ...,
                          expiration: int = 3600) -> str:
        """Генерирует пре-подписанный url для файла из s3 хранилища

        :param filename: Название файла
        :type filename: str
        :param content_type: Тип возвращаемого контента (audio/mp3, video/mp4, image/jpeg)
        :type content_type: str
        :param content_disposition: Значение Content-Disposition ("inline" или "attachment")
        :type content_disposition: str
        :param expiration: Время действия url в секундах (по умолчанию 1 час)
        :type expiration: int
        :param default: Вернуть данное значение, если файл с таким именем не существует и проигнорировать исключение
        :type default: Any
        :raises ValueError: Если файл с таким именем не существует
        :return: Пре-подписанный url
        :rtype: str
        """
        if not self._file_exists(filename):
            if default is not ...:
                return default
            raise ValueError(f"File not found: {filename}")

        url = self._s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": filename,
                "ResponseContentType": content_type,
                "ResponseContentDisposition": content_disposition
            },
            ExpiresIn=expiration
        )

        return url

    def get_file_url_fast(self, filename: str,
                          content_type: str,
                          content_disposition: str,
                          expiration: int = 3600):
        """Генерирует пре-подписанный url для файла из s3 хранилища.\n
        Внимание! Данный метод не проверяет существование файла в s3 хранилище. Если файл отсутствует в хранилище,
        то при переходе по сгенерированной ссылке будет xml с ошибкой. Используйте данный метод, если абсолютно точно
        уверены, что файл существует в s3 хранилище

        :param filename: Название файла
        :type filename: str
        :param content_type: Тип возвращаемого контента (audio/mp3, video/mp4, image/jpeg)
        :type content_type: str
        :param content_disposition: Значение Content-Disposition ("inline" или "attachment")
        :type content_disposition: str
        :param expiration: Время действия url в секундах (по умолчанию 1 час)
        :type expiration: int
        :return: Пре-подписанный url
        :rtype: str
        """

        url = self._s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": filename,
                "ResponseContentType": content_type,
                "ResponseContentDisposition": content_disposition
            },
            ExpiresIn=expiration
        )

        return url

    def get_file_urls(self,
                      *filenames: str,
                      content_type: str,
                      content_disposition: str,
                      expiration: int = 3600) -> list[str]:
        """Генерирует пре-подписанные url для файлов из s3 хранилища.\n
        Внимание! Данный метод использует быстрый способ генерации url. См. документацию к методу _get_file_url_fast

        :param filenames:
        :param content_type:
        :param content_disposition:
        :param expiration:
        :return:
        """
        with ThreadPoolExecutor(max_workers=32) as executor:
            urls = list(
                executor.map(
                    lambda filename: self.get_file_url_fast(
                        filename,
                        content_type=content_type,
                        content_disposition=content_disposition,
                        expiration=expiration
                    ),
                    filenames
                )
            )
        return urls

    def get_file_group_urls(self,
                            *sequences: Sequence[str],
                            content_types: Sequence[str],
                            content_disposition: str,
                            expiration: int = 3600) -> list[list[str]]:
        """Генерирует пре-подписанные URL для групп файлов из S3 хранилища.

            :param sequences: Последовательность последовательностей имен файлов.
            Каждая внутренняя последовательность представляет собой группу файлов, для которых нужно сгенерировать URL.
            :type sequences: Sequence[Sequence[str]]
            :param content_types: Последовательность content types, соответствующих файлам в ``sequences``.
            Длина ``content_types`` должна быть равна длине каждой внутренней последовательности в ``sequences``.
            :type content_types: Sequence[str]
            :param content_disposition: Значение Content-Disposition для пре-подписанных URL.
            :type content_disposition: str
            :param expiration: Срок действия пре-подписанных URL в секундах.  По умолчанию 3600 (1 час).
            :type expiration: int, optional
            :return: Список списков URL. Каждый внутренний список содержит URL для файлов в соответствующей группе.
            :rtype: list[list[str]]"""
        with ThreadPoolExecutor(max_workers=32) as executor:
            urls = list(
                executor.map(
                    lambda sequence: list(
                        map(
                            lambda filename, content_type: self.get_file_url_fast(
                                filename,
                                content_type=content_type,
                                content_disposition=content_disposition,
                                expiration=expiration
                            ),
                            sequence,
                            content_types
                        )
                    ),
                    sequences
                )
            )
        return urls

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
