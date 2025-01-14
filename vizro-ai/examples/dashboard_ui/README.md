```bash
docker buildx build --platform linux/amd64 \
  -t vizro-ai-ui-for-dashboard:0.0.1 \
  -t vizro-ai-ui-for-dashboard:latest \
  --load \
  .
```

(local distribution only)
```bash
docker save vizro-ai-ui-for-dashboard:latest -o image.tar
docker load -i image.tar
```


```bash
docker run -p 7868:7868 -p 8051:8051 vizro-ai-ui-for-dashboard:latest
```

