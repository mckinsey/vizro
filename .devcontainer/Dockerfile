FROM mcr.microsoft.com/devcontainers/base:debian

WORKDIR /tmp/scripts/
COPY install-hatch.sh .
RUN chmod +x install-hatch.sh && ./install-hatch.sh && rm install-hatch.sh

USER vscode
RUN echo "alias hr='hatch run'" >> ~/.bashrc
