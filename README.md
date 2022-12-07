# ml_project1

Start Machine Learning Project:

Requirements:

1. [Github Account](https://github.com/)
2. [Heroku Account](https://id.heroku.com/login)
3. [VS Code IDE](https://code.visualstudio.com/download)
4. [GIT CLI](https://git-scm.com/downloads)
5. [GIT Documentation](https://git-scm.com/docs/gittutorial)
---

### Creating conda environment
```
conda create -p venv python==3.7 -y
```

### Activate newly created conda environment
```
conda activate venv/
```

### Installing requirements.txt
```
pip install -r requirements.txt
```

### To add files to git
```
git add .
```
OR
```
git add <file_name>
```

### To check which files are added
```
git status
```

### To ignore some files or folders from uploading in git write those file/folder names in `.gitignore` file.

---

### To create version/commit of all changes by git
```
git commit -m "custom message"
```

### To check all version maintained by git
```
git log
```

### To check remote url
```
git remote -v
```

### To check branches available at git
```
git branch
```

### To send version/changes to github
```
git push origin main
```

----

### To setup CI/CD pipeline in heroku we need 3 information

1. HEROKU_EMAIL = 
2. HEROKU_API_KEY = 
3. HEROKU_APP_NAME = 

---
### To run docker deployment locally following steps can perform if docker is installed in system
<br>

### To check docker is installed or not
```
docker --version
```

### BUILD DOCKER IMAGE
`docker build -t <image_name>:<tagname> .`
> Note: Image name for docker must be lowercase
```
docker built -t ml-project:latest .
```

### To list docker images
```
docker images
```

### To run docker image
requirement: <IMAGE_ID>
```
docker run -p 5000:5000 -e PORT=5000 <IMAGE_ID>
```

### To check running container in docker
```
docker ps
```

### To stop running container
requirement:<CONTAINER_ID>
```
docker stop <CONTAINER_ID>
```






