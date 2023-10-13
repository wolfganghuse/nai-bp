#!/bin/bash

if [ '@@{calm_array_index}@@' != '0' ];
then exit 0
fi

echo "Getting the NAI LLM Version @@{NAI_LLM_REVISION}@@"

export WORK_DIR="/home/ubuntu/nai-release-@@{NAI_LLM_REVISION}@@"
mkdir $WORK_DIR

curl -O -L "https://github.com/nutanix/nai-llm/archive/v@@{NAI_LLM_REVISION}@@.tar.gz" > "v@@{NAI_LLM_REVISION}@@.tar.gz"
echo "Unzipping the NAI LLM Version @@{NAI_LLM_REVISION}@@"
tar -xvf v@@{NAI_LLM_REVISION}@@.tar.gz -C $WORK_DIR --strip-components=1
pip3 install -r $WORK_DIR/llm/requirements.txt
### needs to be done for 0.1 release
sudo chmod +x $WORK_DIR/llm/run.sh