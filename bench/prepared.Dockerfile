ARG BASE_IMAGE
FROM nixos/nix:2.31.2@sha256:29fc5fe207f159ceb0143c25c19c774062fee02ce5eda118f3067547b3054894 AS nix
FROM ${BASE_IMAGE}
COPY --from=nix /nix /nix
ENV PATH="/root/.nix-profile/bin:/nix/var/nix/profiles/default/bin:${PATH}"
RUN mkdir -p /etc/nix && printf '%s\n' 'experimental-features = nix-command flakes' \
    'sandbox = false' 'build-users-group =' > /etc/nix/nix.conf
WORKDIR /app
COPY . /app/
RUN git init -q -b main && bash infra/nix/install-devenv.sh && devenv shell -- just setup
RUN devenv shell -- sh -c 'readlink -f .devenv/profile > /etc/exordio-profile'
# Apply the pinned upstream instrumentation to the image-local Python installation.
RUN if test -x /app/src/python/.venv/bin/python; then \
      PATH="$(cat /etc/exordio-profile)/bin:$PATH" python3 /opt/cbrun/access_monitor.py --install-hooks; \
    fi
# The native judge overlays the submitted tree on /app in a fresh image.
RUN tar -C /app -cf /opt/exordio-starter.tar . && find /app -mindepth 1 -delete
