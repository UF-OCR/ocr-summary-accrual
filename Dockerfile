# INSTALL PYTHON IMAGE
FROM python:3.6
MAINTAINER Christopher "cshannon@ufl.edu"

# INSTALL TOOLS
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 7000
CMD python ./app.py
