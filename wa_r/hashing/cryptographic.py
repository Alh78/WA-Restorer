import wa_r.constants
import wa_r.types
import hashlib

FILE_HASHING_ALGORITHMS = {wa_r.types.FileHashingAlgorithm.SHA256: hashlib.sha256}


def generate_file_content_hash(file_name: str, hashing_algorithm: wa_r.types.FileHashingAlgorithm = wa_r.constants.DEFAULT_FILE_HASHING_ALGORITHM, chunk_size: int = wa_r.constants.DEFAULT_FILE_READING_CHUNK_SIZE) -> bytes:
    hashing_instance = FILE_HASHING_ALGORITHMS.get(hashing_algorithm)
    
    with open(file_name, "rb") as file_handle:
        while content_chunk := file_handle.read(chunk_size):
            hashing_instance.update(content_chunk)

    return hashing_instance.digest()
