# Get the base Python Image from Docker Hub
FROM python:3.10.6

# Set the working directory to /app
WORKDIR /

# pyodbc
RUN apt-get update
RUN apt-get install g++ unixodbc-dev -y
RUN pip install --user pyodbc==4.0.39

# mssql
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18
# RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
RUN . ~/.bashrc

# Copy the current directory contents into the container at /app
COPY labels/requirements-labels.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements-labels.txt

# Copy the current directory contents into the container at /app
COPY labels/ labels/

# Expose the port
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "-m", "labels.api"]