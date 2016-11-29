#!/bin/bash -xe

GH_ORG=jenkins-infra

if [ $1 -ne "" ]; then
    GH_ORG=$1
fi;

OUTPUT_DIR=${GH_ORG}-megalith.git

if [ ! -f repos ]; then
    echo "Fetching repositories for ${GH_ORG}"
    python fetch-repos.py ${GH_ORG}
fi;

mkdir -p ${OUTPUT_DIR}

pushd ${OUTPUT_DIR}

    if [ ! -d '.git' ]; then
        echo "Making sure megalith is a git repository"
        git init
    fi;

    for REPO in $(cat ../repos); do
        echo "Processing: ${REPO}"
        git fetch --no-tags \
            git://github.com/${GH_ORG}/${REPO}.git \
            "+refs/heads/*:refs/heads/${REPO}/*" \
            "+refs/tags/*:refs/tags/${REPO}/*"
    done;

popd
