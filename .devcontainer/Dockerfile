FROM mcr.microsoft.com/devcontainers/base:debian

WORKDIR /tmp/scripts/
COPY install-hatch.sh .
RUN chmod +x install-hatch.sh
RUN ./install-hatch.sh
RUN install-hatch.sh

RUN hatch python install 3.11