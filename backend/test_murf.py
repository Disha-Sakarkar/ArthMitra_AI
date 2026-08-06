from app.services.murf_service import generate_audio

audio = generate_audio("Hello, I am Swasthya Saathi.")

for i, chunk in enumerate(audio):
    print(i, type(chunk))

    if i == 2:
        break