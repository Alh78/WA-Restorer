import wa_r.constants


def generate_file_content_hash(file_name: str, chunk_size: int = wa_r.constants.DEFAULT_MEDIA_CHUNK_SIZE) -> bytes:
    hashing_instance = wa_r.constants.DEFAULT_FILE_HASHING_ALGORITHM()
    
    with open(file_name, "rb") as file_handle:
        while content_chunk := file_handle.read(chunk_size):
            hashing_instance.update(content_chunk)

    return hashing_instance.digest()