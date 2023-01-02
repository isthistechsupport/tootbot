docker buildx build \
    --platform linux/amd64,linux/arm64,linux/arm/v7,linux/386 \
    -t isthistechsupport/tootbot:latest \
    -t isthistechsupport/tootbot:3 \
    -t isthistechsupport/tootbot:3.0 \
    -t isthistechsupport/tootbot:3.0.1 \
    --push \
    -f ./Dockerfile .
