import os

from django.test import mock, override_settings

from .. import fields
from .. import models
from .. import image_data

from .models import ImageTestCase
from .utils import patch_settings

class TestGalleryImageFieldFile(ImageTestCase):

    def setUp(self):
        super().setUp()
        with mock.patch.object(image_data, 'InMemoryImageData') as m:
            with mock.patch.object(image_data, 'ImageFile') as f:
                with patch_settings(
                    {
                        'image_width': 1024,
                        'image_height': 768,
                        'small_image_width': 800,
                        'small_image_height': 600,
                        'preview_width': 400,
                        'preview_height': 300,
                        'small_preview_width': 200,
                        'small_preview_height': 150,
                        'thumbnail_width': 120,
                        'thumbnail_height': 80
                    }
                ):
                    self.field_file = fields.GalleryImageFieldFile(
                        self.image,
                        mock.MagicMock(),
                        str(self.image)
                    )
            self.image_file = f
            self.in_memory_data = m

    def test_init(self):
        self.in_memory_data.assert_any_call(
            self.field_file,
            1024,
            768
        )
        self.image_file.assert_any_call(
            self.field_file,
            800,
            600,
            'small'
        )
        self.image_file.assert_any_call(
            self.field_file,
            200,
            150,
            'small_preview'
        )
        self.image_file.assert_any_call(
            self.field_file,
            120,
            80,
            'thumbnail'
        )
        self.image_file.assert_any_call(
            self.field_file,
            400,
            300,
            'preview'
        )

    @override_settings(MEDIA_ROOT='/media')
    @mock.patch('os.mkdir')
    @mock.patch('os.path.isdir', return_value=True)
    def test_check_dir_exists(self, isdir, mkdir):
        path = '/media' + os.sep + 'gallery'
        with patch_settings({'path': 'gallery'}):
            self.field_file._check_dir()
        isdir.assert_called_width(path)
        mkdir.assert_not_called()

    @override_settings(MEDIA_ROOT='/media')
    @mock.patch('os.mkdir')
    @mock.patch('os.path.isdir', return_value=False)
    def test_check_dir_does_not_exist(self, isdir, mkdir):
        path = '/media' + os.sep + 'gallery'
        with patch_settings({'path': 'gallery'}):
            self.field_file._check_dir()
        isdir.assert_called_width(path)
        mkdir.assert_called()

    def test_save_files_image_data_exists(self):
        self.field_file._check_dir = mock.MagicMock()
        self.field_file.image_data.data = True
        self.field_file.image_data.name_in_db = 'foo'
        self.field_file.save_files('bar', 'baz')

        self.field_file._check_dir.assert_called()
        self.field_file.image_data.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.thumbnail.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.preview.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.small_preview.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.small_image.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.assertEqual(self.field_file.name, str(self.image))

    def test_save_files_image_data_does_not_exist(self):
        self.field_file._check_dir = mock.MagicMock()
        self.field_file.image_data.data = None
        self.field_file.image_data.name_in_db = 'foo'
        self.field_file.save_files('bar', 'baz')

        self.field_file._check_dir.assert_called()
        self.field_file.image_data.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.thumbnail.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.preview.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.small_preview.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.small_image.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.assertEqual(self.field_file.name, 'foo')

    def test_delete_files(self):
        self.field_file.delete_files()
        self.field_file.image_data.delete.assert_called()
        self.field_file.thumbnail.delete.assert_called()
        self.field_file.preview.delete.assert_called()
        self.field_file.small_preview.delete.assert_called()
        self.field_file.small_image.delete.assert_called()

    def test_thumbnail_url(self):
        url = self.field_file.thumbnail_url
        self.assertEqual(url, self.field_file.thumbnail.url)

    def test_image_url(self):
        url = self.field_file.image_url
        self.assertEqual(url, self.field_file.image_data.url)

    def test_smal_image_url(self):
        url = self.field_file.small_image_url
        self.assertEqual(url, self.field_file.small_image.url)

    def test_preview_url(self):
        url = self.field_file.preview_url
        self.assertEqual(url, self.field_file.preview.url)

    def test_small_preview_url(self):
        url = self.field_file.small_preview_url
        self.assertEqual(url, self.field_file.small_preview.url)
