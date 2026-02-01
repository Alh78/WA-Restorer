import mutagen.mp4
import wa_r.types
import datetime
import piexif
import shutil
import os


def read_file_message_lines(file_name: str):
    with open(file_name, mode = "r", encoding = "utf-8") as file_handle:
        file_handle.seek(0)
        while file_content_chunk := file_handle.readline():
            yield file_content_chunk


def write_new_exif_data(source: str,
                        destination: str,
                        exif_data: wa_r.types.WPMediaMetaData,
                        add_owner: bool = False,
                        edit_file_dates: bool = True):
    if os.path.splitext(source)[-1].lower() in [".png", ".jpg", ".jpeg"]:
        dumped_timestamp = exif_data.timestamp.strftime("%Y:%m:%d %H:%M:%S")

        zeroth_ifd = {piexif.ImageIFD.DateTime: dumped_timestamp,
                      piexif.ImageIFD.ImageDescription: u"Restored from Whatsapp Backup"}

        if exif_data.device_brand is not None:
            zeroth_ifd[piexif.ImageIFD.Make] = exif_data.device_brand
        
        if exif_data.device_model is not None:
            zeroth_ifd[piexif.ImageIFD.Model] = exif_data.device_model

        if add_owner:
            zeroth_ifd[piexif.ImageIFD.Artist] = exif_data.owner.encode("utf-8")

        exif_ifd = {piexif.ExifIFD.DateTimeOriginal: dumped_timestamp,
                    piexif.ExifIFD.DateTimeDigitized: dumped_timestamp,
                    piexif.ExifIFD.OffsetTimeOriginal: "+3",
                    piexif.ExifIFD.OffsetTimeDigitized: "+3",
                    piexif.ExifIFD.OffsetTime: str(wa_r.constants.UTC_TIME_OFFSET) if wa_r.constants.UTC_TIME_OFFSET <= 0 else "+" + str(wa_r.constants.UTC_TIME_OFFSET)}

        exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd} # piexif.dump completes the remaining fields as blank areas.

        shutil.copy2(source, destination)
        piexif.insert(piexif.dump(exif_dict), destination)

    elif os.path.splitext(source)[-1].lower() in [".mp4", ".m4v", ".mov"]:
        dumped_timestamp = exif_data.timestamp.replace(tzinfo = datetime.timezone(datetime.timedelta(hours = 3))) #!

        shutil.copy2(source, destination)

        media_video_handle = mutagen.mp4.MP4(destination)

        media_video_handle["\xa9day"] = dumped_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        media_video_handle["----:com.apple.quicktime:creationdate"] = [dumped_timestamp.isoformat().encode("utf-8")]
        media_video_handle["\xa9cmt"] = "Restored from Whatsapp Backup"

        if add_owner:
            media_video_handle["\xa9ART"] = exif_data.owner

        media_video_handle.save()

    if edit_file_dates:
        os.utime(destination, (exif_data.timestamp.timestamp(), exif_data.timestamp.timestamp()))


