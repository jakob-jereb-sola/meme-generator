FROM python:3.14

WORKDIR /meme_generetor

COPY . .

RUN pip install flask pillow

ENV PORT=5000

EXPOSE 5000

CMD [ "python", "meme_generator.py" ]