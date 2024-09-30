docker build --no-cache \
    -t isthistechsupport/tootbot:latest \
    -t isthistechsupport/tootbot:3 \
    -t isthistechsupport/tootbot:3.1 \
    -t isthistechsupport/tootbot:3.1.2 . && \
docker image prune -f && \
docker push -a isthistechsupport/tootbot
