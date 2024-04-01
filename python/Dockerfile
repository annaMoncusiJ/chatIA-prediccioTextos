FROM python:3.11

WORKDIR /usr/src/app
EXPOSE 5000

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#COPY tensorflow-2.15.0 /tensorflow-2.15.0

#WORKDIR /tensorflow-2.15.0/tensorflow/tools/pip_package/redundant_tensorflow_gpu/
#RUN pip install .

# Volver al directorio de trabajo principal
#WORKDIR /usr/src/app

COPY . ./

CMD [ "python", "./testGit.py" ]

