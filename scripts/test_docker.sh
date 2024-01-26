docker build -t dashboard-app --platform linux/amd64 -f dashboard/Dockerfile .
docker run -p 8000:8050 --env-file dashboard/.dashboard.env --platform linux/amd64 dashboard-app
