import wa_r.constants
import numpy as np
import wa_r.types
import PIL.Image
import videohash
import imagehash


IMAGE_HASHING_ALGORITHMS = {wa_r.types.ImageHashingAlgorithm.PHASH: imagehash.phash,
                            wa_r.types.ImageHashingAlgorithm.AHASH: imagehash.average_hash,
                            wa_r.types.ImageHashingAlgorithm.WHASH: imagehash.whash}


VIDEO_HASHING_ALGORITHMS = {wa_r.types.VideoHashingAlgorithm.WHASH: videohash.VideoHash} # Official documentation of library states that they use whash algorithm
                                                                                         # and also doesn't have any support for other libraries.
                                                                                         # New code writings might be implemented for optimization.


def generate_image_content_hash(file_name: str,
                                hashing_algorithm: wa_r.types.ImageHashingAlgorithm = wa_r.constants.DEFAULT_IMAGE_HASHING_ALGORITHM,
                                hash_size: int = wa_r.constants.DEFAULT_IMAGE_HASH_SIZE) -> bytes: #Normalize output
    with PIL.Image.open(file_name) as image_file:
        hash_instance = IMAGE_HASHING_ALGORITHMS.get(hashing_algorithm)(image_file, hash_size) 
        return np.packbits(hash_instance.hash).tobytes()


def generate_video_content_hash(file_name: str,
                                hashing_algorithm: wa_r.types.VideoHashingAlgorithm = wa_r.constants.DEFAULT_VIDEO_HASHING_ALGORITHM) -> videohash.VideoHash: # Normalize output
    return VIDEO_HASHING_ALGORITHMS.get(hashing_algorithm)(path = file_name)
    


