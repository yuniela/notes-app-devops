FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#Create an app directory
WORKDIR /app

#install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Copy project files
COPY . .

#Expose Flask port
EXPOSE 5000

#Star app
CMD ["flask", "run", "--host=0.0.0.0"]


