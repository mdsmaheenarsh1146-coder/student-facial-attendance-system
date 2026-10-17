from deepface import DeepFace
import tempfile
import os


def verify_face(uploaded_image, reference_path):
    current_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".jpg",
            delete=False
        ) as file:
            for chunk in uploaded_image.chunks():
                file.write(chunk)

            current_path = file.name

        result = DeepFace.verify(
            img1_path=reference_path,
            img2_path=current_path,
            model_name="VGG-Face",
            detector_backend="retinaface",
            distance_metric="cosine",
            enforce_detection=True,
            align=True,
        )

        return bool(result["verified"])

    except ValueError as e:
        if "Face could not be detected" in str(e):
            return False
        raise

    finally:
        if current_path and os.path.exists(current_path):
            os.remove(current_path)