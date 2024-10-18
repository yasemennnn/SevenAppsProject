import os
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from PIL import Image

from moviepy.config import change_settings

# ImageMagick binary yolunu belirtinme
change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16\magick.exe"}
)


def find_green_area(frame):
    # Görüntüyü HSV renk uzayına çevir
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Yeşil renk için HSV aralıkları
    lowerGreen = np.array([40, 40, 40])
    upperGreen = np.array([70, 255, 255])

    # Find Green Area
    mask = cv2.inRange(hsvFrame, lowerGreen, upperGreen)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largestContour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largestContour)
        return (x, y, w, h)
    else:
        return None


def overlay_image_on_dynamic_green_area(clip, image_path):

    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    def add_image_to_frame(get_frame, t):
        frame = get_frame(t)

        greenArea = find_green_area(frame)

        if greenArea:
            x, y, w, h = greenArea

            resized_img = cv2.resize(img, (w, h))
            img_pil = Image.fromarray(cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGBA))

            frame_pil = Image.fromarray(frame)
            frame_pil.paste(img_pil, (x, y), img_pil)

            return np.array(frame_pil)
        else:
            return frame

    new_clip = clip.fl(add_image_to_frame)
    return new_clip


def add_title_to_video(clip, title_text):
    txt_clip = TextClip(title_text, fontsize=50, color="white")
    txt_clip = txt_clip.set_position((0.3, 0.3), relative=True).set_duration(
        clip.duration
    )

    final_clip = CompositeVideoClip([clip, txt_clip])
    return final_clip


def process_video_with_images_and_titles(video_path, images, titles):
    clip = VideoFileClip(video_path)

    for image, title in zip(images, titles):
        try:
            new_clip = overlay_image_on_dynamic_green_area(clip, image)

            titled_clip = add_title_to_video(new_clip, title)

            titled_clip.write_videofile(f"localized_video_{title}.mp4", codec="libx264")

        except FileNotFoundError as e:
            print(f"Dosya bulunamadı: {e}")
        except Exception as e:
            print(f"Bir hata oluştu: {e}")


project_dir = os.path.dirname(os.path.abspath(__file__))  # Projenin bulunduğu dizin
video_path = os.path.join(project_dir, "video.mp4")

photo1_path = os.path.join(project_dir, "a.jpg")
photo2_path = os.path.join(project_dir, "b.jpg")
photo3_path = os.path.join(project_dir, "c.jpg")

# video_path = video_path

images = [
    photo1_path,
    photo2_path,
    photo3_path,
]  # Resim dosyalarının pathleri
titles = [
    "Birds Are Singing",
    "Basketball Player Is Shooting",
    "Near Sea Into Palms",
]  # Başlıklar


process_video_with_images_and_titles(video_path, images, titles)
