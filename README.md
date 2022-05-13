# MusicLink
Link for Plex, Lidarr, Discogs, Youtube

### **Celery:**

To launch celery during development on Windows, use the following command:

`celery -A app.celery worker -l info --pool=solo`

### **Redis:**

To install Redis (Required for the functioning of Celery) in a docker, use the following command:

`docker run --name my-redis -p 6379:6379 -d redis`