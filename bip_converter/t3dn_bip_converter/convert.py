import io
from typing import Union
from pathlib import Path
from PIL import Image
from zlib import compress, decompress


def convert_file(src: Union[str, Path], dst: Union[str, Path] = None):
    '''Convert between BIP and various image formats.'''
    src = Path(src).resolve()
    src_bip = src.suffix.lower() == '.bip'

    if dst is not None:
        dst = Path(dst).resolve()
        dst_bip = dst.suffix.lower() == '.bip'
    else:
        dst = src.with_suffix('.png' if src_bip else '.bip')
        dst_bip = not src_bip

    if not src_bip and dst_bip:
        _image_to_bip(src, dst)
    elif src_bip and not dst_bip:
        _bip_to_image(src, dst)
    else:
        raise ValueError('exactly one file must be in BIP format')


def _image_to_bip(src: Union[str, Path], dst: Union[str, Path]):
    '''Convert various image formats to BIP.'''
    with Image.open(src) as image:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        if not image.mode.endswith(('A', 'a')):
            image = image.convert('RGBA')
        elif image.mode != 'RGBa':
            image = image.convert('RGBa')

        images = [image.resize(size=(32, 32)), image]
        contents = [compress(image.tobytes()) for image in images]

        with open(dst, 'wb') as output:
            output.write(b'BIP2')
            output.write(len(images).to_bytes(1, 'big'))

            for image, content in zip(images, contents):
                width, height = image.size
                output.write(width.to_bytes(2, 'big'))
                output.write(height.to_bytes(2, 'big'))
                output.write(len(content).to_bytes(4, 'big'))

            for content in contents:
                output.write(content)


def _bip_to_image(src: Union[str, Path], dst: Union[str, Path]):
    '''Convert BIP to various image formats.'''
    with open(src, 'rb') as bip:
        if bip.read(4) != b'BIP2':
            raise ValueError('input is not a supported file format')

        count = int.from_bytes(bip.read(1), 'big')
        bip.seek(8 * (count - 1), io.SEEK_CUR)

        width = int.from_bytes(bip.read(2), 'big')
        height = int.from_bytes(bip.read(2), 'big')
        length = int.from_bytes(bip.read(4), 'big')

        bip.seek(-length, io.SEEK_END)
        content = decompress(bip.read())

        image = Image.frombytes('RGBa', (width, height), content)
        image = image.convert('RGBA')
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        try:
            image.save(dst)
        except OSError:
            image.convert('RGB').save(dst)