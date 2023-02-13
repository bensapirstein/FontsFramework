import unittest
import pandas as pd
import os
import data.data_collection as font_downloader
import shutil
import pymongo

class TestFontDownloader(unittest.TestCase):
    def setUp(self):
        self.api_key = "AIzaSyCi-x8BDFvabHoFdNy9kcqpIfPPIgkz0p4"
        self.font_folder = "test_fonts"
        self.num_fonts = 1
        self.categories = ["sans-serif"]
        self.subsets = ["latin"]
        self.ufo_collection = None
        self.data_file = "test_data.csv"
        self.client = pymongo.MongoClient("mongodb+srv://test:M3NQXAb2mSBdsjsa@cluster0.slwp6m3.mongodb.net/test")
        self.db = self.client["test_database"]
        self.ufos_collection = self.db["ufos"]

    def test_get_fonts_info(self):
        # Test that the function returns a DataFrame
        fonts_df = font_downloader.get_fonts_info(self.api_key)
        self.assertIsInstance(fonts_df, pd.DataFrame)

    def test_filter_fonts(self):
        # Test that the function filters the DataFrame correctly
        fonts_df = font_downloader.get_fonts_info(self.api_key)
        filtered_df = font_downloader.filter_fonts(fonts_df, num_fonts=self.num_fonts, categories=self.categories, subsets=self.subsets)
        self.assertEqual(filtered_df.shape[0], self.num_fonts)
        self.assertTrue(all(filtered_df["category"].isin(self.categories)))
        self.assertTrue(all(filtered_df["subsets"].apply(lambda x: any(lang in x for lang in self.subsets))))
        self.assertEqual(filtered_df["subsets"].shape[0], self.num_fonts)

    def test_download_fonts(self):
        # Test that the function downloads the fonts and returns a DataFrame
        fonts_df = font_downloader.get_fonts_info(self.api_key)
        filtered_df = font_downloader.filter_fonts(fonts_df, num_fonts=self.num_fonts, categories=self.categories, subsets=self.subsets)
        downloaded_df = font_downloader.download_fonts(filtered_df, self.font_folder)
        self.assertIsInstance(downloaded_df, pd.DataFrame)
        self.assertEqual(downloaded_df.shape[0], filtered_df.shape[0])
        self.assertTrue(all(downloaded_df["file_path"].apply(lambda x: all(os.path.exists(path) for path in x))))

    def test_convert_df_to_ufo(self):
        # Test that the function converts the fonts to UFO format and returns a DataFrame
        fonts_df = font_downloader.get_fonts_info(self.api_key)
        filtered_df = font_downloader.filter_fonts(fonts_df, num_fonts=self.num_fonts, categories=self.categories,
                                                   subsets=self.subsets)
        downloaded_df = font_downloader.download_fonts(filtered_df, self.font_folder)
        downloaded_df.to_csv(self.data_file)
        converted_df = font_downloader.convert_df_to_ufo(self.data_file, self.font_folder)
        self.assertIsInstance(converted_df, pd.DataFrame)
        self.assertEqual(converted_df.shape[0], downloaded_df.shape[0])
        self.assertTrue(all(converted_df["variants"].apply(lambda x: all(os.path.exists(x[variant]) for variant in x) )))

    def test_upload_ufos(self):
        # Test that the function uploads the UFO files to the specified bucket
        fonts_df = font_downloader.get_fonts_info(self.api_key)
        #filtered_df = font_downloader.filter_fonts(fonts_df, num_fonts=self.num_fonts, categories=self.categories, subsets=self.subsets)
        filtered_df = fonts_df[fonts_df['family'] == 'M PLUS Code Latin']
        downloaded_df = font_downloader.download_fonts(filtered_df, self.font_folder)
        downloaded_df.to_csv(self.data_file)
        converted_df = font_downloader.convert_df_to_ufo(self.data_file, self.font_folder)

        # Upload UFO files to the DB
        failed_cases = font_downloader.upload_ufos(self.ufos_collection)

        # Check if all the UFO files are uploaded to the DB
        for _, row in converted_df.iterrows():
            family = row['family']
            variants = row['variants']

            for variant in variants:
                self.assertIsNotNone(self.ufos_collection.find_one({'family': family, 'variant': variant}))

        if failed_cases:
            print("Failed cases:")
            for failed_case in failed_cases:
                print(f"Family: {failed_case['family']}, Variant: {failed_case['variant']}, Error: {failed_case['error']}")

    def test_filter_fonts_with_existing_fonts(self):
        # Download some fonts
        fonts_df = font_downloader.get_fonts_info(self.api_key)
        filtered_df = font_downloader.filter_fonts(fonts_df, num_fonts=1)
        downloaded_df = font_downloader.download_fonts(filtered_df, self.font_folder)
        downloaded_df.to_csv(self.data_file)
        converted_df = font_downloader.convert_df_to_ufo(self.data_file, self.font_folder)

        # Upload UFO files to the DB
        failed_cases = font_downloader.upload_ufos(self.ufos_collection)

        # Check if all the UFO files are uploaded to the DB
        for _, row in converted_df.iterrows():
            family = row['family']
            variants = row['variants']

            for variant in variants:
                self.assertIsNotNone(self.ufos_collection.find_one({'family': family, 'variant': variant}))

        # Try to filter fonts again
        filtered_df_2 = font_downloader.filter_fonts(fonts_df, num_fonts=2, ufos_collection=self.ufos_collection)

        # # Assert that the number of fonts in the filtered DataFrame is less than the original number of fonts
        # self.assertLess(filtered_df_2.shape[0], self.num_fonts)
        #
        # # Assert that none of the families in the filtered DataFrame are in the test collection
        # for _, row in filtered_df_2.iterrows():
        #     family = row['family']
        #     self.assertIsNone(self.ufos_collection.find_one({'family': family}))

    def tearDown(self):
        # delete the test folder and test file
        if os.path.exists(self.font_folder):
            shutil.rmtree(self.font_folder)
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

if __name__ == '__main__':
    unittest.main()

