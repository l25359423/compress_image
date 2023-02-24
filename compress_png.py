import argparse
import os
import sys

import tinify

from os import path
from PIL import Image
from tinypng_keys import tinypng_keys


class CompressImage(object):
    tinypng_key_index = 0
    tinypng_use_number = 0

    @classmethod
    def get_tinypng_key(cls):
        if cls.tinypng_use_number == 500:
            cls.tinypng_key_index += 1
            if cls.tinypng_key_index >= len(tinypng_keys-1):
                print("tinypng quota used up, exit")
                sys.exit()
        return tinypng_keys[cls.tinypng_key_index]

    @classmethod
    def compress_by_tinypng(cls, file_path):
        print("Compress by tinypng...")
        tinypng_key = cls.get_tinypng_key()
        print("Tinypng Key: " + tinypng_key)
        print("Tinypng Used: " + (str)(cls.tinypng_use_number))
        tinify.key = tinypng_key
        source = tinify.from_file(file_path)
        source.to_file(file_path)
        cls.tinypng_use_number += 1

    @classmethod
    def compress_image(cls, input_file_path, output_file_path,
                       max_width=1200, max_size=None):
        with Image.open(input_file_path) as image:
            if image.width > max_width:
                scale = max_width / image.width
                new_size = (int(image.width * scale), int(image.height * scale))
                image = image.resize(new_size, resample=Image.Resampling.LANCZOS)
            if image.mode == 'CMYK':
                image = image.convert('RGB')

            quality = 80

            while True:
                image.save(output_file_path, format="PNG", optimize=True,
                           quality=quality, progressive=True, subsampling=0,
                           icc_profile=None, exif=image.info.get('exif'),
                           qtables='web_low', quality_mode='keep')

                if max_size is None:
                    break

                file_size = os.path.getsize(output_file_path)
                if file_size <= int(max_size):
                    print("success")
                    break

                if quality > 80:
                    quality -= 10
                else:
                    print("File Size: %s" % str(file_size/1000))
                    cls.compress_by_tinypng(output_file_path)
                    print("File Size: %s" % str(os.path.getsize(output_file_path) / 1000))
                    break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compress PNG images in a directory')
    parser.add_argument('input', metavar='input', type=str, help='the input directory path')
    parser.add_argument('output', metavar='output', type=str, help='the output directory path')
    parser.add_argument('--max-width', type=int, default=1920, help='the maximum width of the compressed image')

    args = parser.parse_args()
    
    # check dif exist.
    if not os.path.isdir(args.input):
        print(f'Error: {args.input} is not a directory.')
        exit(1)
    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    for filename in os.listdir(args.input):
        print("-" * 40)
        print("File: " + filename)
        input_file_path = path.join(args.input, filename)

        if path.splitext(filename)[1].lower() != '.png':
            continue

        output_file_path = path.join(args.output, filename)

        CompressImage.compress_image(input_file_path, output_file_path, args.max_width, "15000")
        os.remove(input_file_path)
        print(f'{output_file_path}')
        print("-"*40)
        print("")
        print("")

    print(f'Image compression completed. Output directory: {args.output}')

