#!/bin/bash

if [ '@@{calm_array_index}@@' != '0' ]; then
    echo "model download must be run from the first VM in the replica set"
    exit 0
fi

export PATH=$PATH:/home/ubuntu/.local/bin
export WORK_DIR="/home/ubuntu/nai-release-@@{NAI_LLM_REVISION}@@"

MODEL_NAME="@@{AI_MODEL_NAME}@@"
MODEL_REVISION="@@{AI_MODEL_REVISION}@@"

echo $MODEL_NAME
echo $MODEL_REVISION



mkdir -p /mnt/llm/$MODEL_NAME
mkdir -p $WORK_DIR/models/$MODEL_NAME

if [ -z "$MODEL_REVISION" ]; then
    python3 $WORK_DIR/llm/download.py --model_name $MODEL_NAME --model_path $WORK_DIR/models/$MODEL_NAME --mar_output /mnt/llm/$MODEL_NAME

else
    python3 $WORK_DIR/llm/download.py --model_name $MODEL_NAME --model_path $WORK_DIR/models/$MODEL_NAME --mar_output /mnt/llm/$MODEL_NAME --repo_version $MODEL_REVISION

fi

rm -rf $WORK_DIR/models/$MODEL_NAME