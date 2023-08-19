ARG BASE_REGISTRY=registry.access.redhat.com
ARG BASE_IMAGE=ubi8/ubi
ARG BASE_TAG=8.5

#### Start first stage
#### KhulnaSoft wheels, binary dependencies, etc. are staged to /build_output for second stage
FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG} as khulnasoft-cli-builder

ENV LANG=en_US.UTF-8 
ENV LC_ALL=C.UTF-8
ENV PIP_VERSION=21.0.1

COPY . /buildsource
WORKDIR /buildsource

RUN set -ex && \
    mkdir -p \
        /build_output/configs \
        /build_output/deps \
        /build_output/wheels

# install build dependencies
RUN set -ex && \
    echo "installing build dependencies" && \
    yum update -y && \
    yum install -y \
        gcc \
        make \
        python38 \
        python38-wheel && \
    pip3 install pip=="${PIP_VERSION}"

# stage khulnasoft wheels and default configs into /build_output
RUN set -ex && \
    pip3 download -d /build_output/wheels pip=="${PIP_VERSION}" && \
    echo "installing khulnasoft" && \
    pip3 wheel --wheel-dir=/build_output/wheels . && \
    cp ./LICENSE /build_output/ && \
    cp ./docker-entrypoint.sh /build_output/configs/docker-entrypoint.sh

# create p1 buildblob & checksum
RUN set -ex && \
    tar -z -c -v -C /build_output -f /khulnasoft-buildblob.tgz . && \
    sha256sum /khulnasoft-buildblob.tgz > /buildblob.tgz.sha256sum

#### Start second stage
#### Setup and install using first stage artifacts in /build_output
FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG} as khulnasoft-cli-final

ARG CLI_COMMIT
ARG KHULNASOFT_CLI_VERSION="0.9.4"
ARG KHULNASOFT_CLI_RELEASE="r0"

# Container metadata section
LABEL khulnasoft_cli_commit=${CLI_COMMIT} \
      source="https://github.com/khulnasoft-lab/khulnasoft-cli" \
      name="khulnasoft-cli" \
      maintainer="dev@khulnasoft.com" \
      vendor="KhulnaSoft Inc." \
      version=${KHULNASOFT_CLI_VERSION} \
      release=${KHULNASOFT_CLI_RELEASE} \
      summary="KhulnaSoft Engine CLI - python client for use against the khulnasoft-engine container image scanning service, for policy-based security, best-practice and compliance enforcement." \
      description="KhulnaSoft is an open platform for container security and compliance that allows developers, operations, and security teams to discover, analyze, and certify container images on-premises or in the cloud. The KhulnaSoft CLI is a python client that can be used to access and manager KhulnaSoft Engine - the on-prem, OSS, API accessible service that allows ops and developers to perform detailed analysis, run queries, produce reports and define policies on container images that can be used in CI/CD pipelines to ensure that only containers that meet your organization’s requirements are deployed into production."

# Environment variables to be present in running environment
ENV LANG=en_US.UTF-8
ENV LC_ALL=C.UTF-8

# Default values that should be overridden in most cases on each container exec
ENV KHULNASOFT_CLI_USER=""
ENV KHULNASOFT_CLI_PASS=""
ENV KHULNASOFT_CLI_URL=http://localhost:8228/v1/

# Copy artifacts from build step
COPY --from=khulnasoft-cli-builder /build_output /build_output

# install OS dependencies
RUN yum update -y && \
    yum install -y \
        python38 \
        python38-wheel && \
    yum clean all && \
    pip3 install --upgrade --no-index --find-links=/build_output/wheels/ pip

# Setup container default configs and directories
RUN set -ex && \
    groupadd --gid 1000 khulnasoft && \
    useradd --uid 1000 --gid khulnasoft --shell /bin/bash --create-home khulnasoft && \
    mkdir -p /licenses/ && \
    cp /build_output/LICENSE /licenses/ && \
    cp /build_output/configs/docker-entrypoint.sh /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

# Perform the khulnasoft-cli build and install
RUN set -ex && \
    pip3 install --no-index --find-links=./ /build_output/wheels/*.whl && \
    rm -rf \
        /build_output \
        /root/.cache

USER 1000

WORKDIR /khulnasoft-cli

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/bin/bash"]
