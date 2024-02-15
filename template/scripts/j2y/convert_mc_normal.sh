#!/bin/bash

while IFS= read -r eggs; do
  tag="egg-${eggs}"
  input="./eggs/json/minecraft/normal/${tag}.json"
  output="./eggs/yml/minecraft/normal/${tag}.yml"
  python3 tool.py y2j -i "${input}" -o "${output}"
done < egglist