# Marker UI

Marker UI provides a simple web user interface to upload a document 
and convert it to Markdown using the [Marker API](https://github.com/adithya-s-k/marker-api).
Marker API is a RESTful API that allows you to convert PDF, PPT, and DOC files to Markdown. It uses the 
[Marker](https://github.com/VikParuchuri/marker) library to parse the document and extract the text and images.

## Docker Usage

### Docker image
- Build the marker-ui docker image with:
```
git clone https://github.com/cahya-wirawan/marker-ui.git
cd marker-ui
docker build -t marker-ui .
```

- Or just pull the pre-built marker-ui docker image with:
```
docker pull wirawan/marker-ui
```

### Docker run
- Prepare an environment file (i.e. ".env") with the content MARKER_API_URL=https://marker-api... (replace the url with your marker-api url)
- run the marker-ui docker container with:
```
docker run --rm -env-file `pwd`/.env -p8000:8000 wirawan/marker-ui
```

## How to use this Marker UI
1. Upload a PDF, PPT, or DOC file.
2. Click on "Convert Document".
3. View the extracted Markdown and images.
4. Download the Markdown file and images.

## Marker API
The marker-api docker image is also available at https://hub.docker.com/repository/docker/wirawan/marker-api


