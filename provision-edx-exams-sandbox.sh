name="edx_exams"
port="18740"

docker-compose -f docker-compose.sandbox.yml up -d --build

# Install requirements
# Can be skipped right now because we're using the --build flag on docker-compose. This will need to be changed once we move to devstack.

# Wait for MySQL
echo "Waiting for MySQL"
until docker exec -i edx_exams.db mysql -u root -se "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'root')" &> /dev/null
do
  printf "."
  sleep 1
done
sleep 5

# Create the database
docker exec -i edx_exams.db mysql -u root -se "CREATE DATABASE edx_exams;"

# Run migrations
echo -e "${GREEN}Running migrations for ${name}...${NC}"
docker exec -t edx_exams.app bash -c "cd /edx/app/edx-exams/ && python3 manage.py migrate"

# Run collectstatic
echo -e "${GREEN}Running collectstatic for ${name}...${NC}"
docker exec -t edx_exams.app bash -c "cd /edx/app/edx-exams/ && python3 manage.py collectstatic"

# Create superuser
echo -e "${GREEN}Creating super-user for ${name}...${NC}"
docker exec -t edx_exams.app bash -c "echo 'from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(\"edx\", \"edx@example.com\", \"edx\") if not User.objects.filter(username=\"edx\").exists() else None' | python /edx/app/edx-exams/manage.py shell"
