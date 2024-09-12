# Train

_Prepare repository_

```console
git clone https://github.com/thewh1teagle/optispeech -b he
cd optispeech
```


Prerequisites

Rye https://rye.astral.sh/

```console
export RYE_INSTALL_OPTION="--yes" 
curl -sSf https://rye.astral.sh/get | bash
echo 'source "$HOME/.rye/env"' >> ~/.bashrc
source "$HOME/.rye/env"
```

__Ubuntu dependencies__

```console
bash -c "$(wget -O - https://apt.llvm.org/llvm.sh)"
sudo apt install cmake nvtop htop p7zip-full -y
sudo ln -s /usr/bin/clang-18 /usr/bin/clang
sudo ln -s /usr/bin/clang++-18 /usr/bin/clang++
```

__Install dependencies__

```console
rye sync
```

_Prepare dataset_

```console
wget "https://openslr.elda.org/resources/134/saspeech_gold_standard_v1.0.tar.gz"
tar xf saspeech_gold_standard_v1.0.tar.gz
```

_Split validation (10%)_ 

```console
# Remove invalid wav file from dataset
sed -i '/^gold_000_line_104/d' saspeech_gold_standard/metadata.csv
cp saspeech_gold_standard/metadata.csv saspeech_gold_standard/metadata.csv.bak
sed -n '1,1000p' saspeech_gold_standard/metadata.csv > saspeech_gold_standard/new.csv && mv saspeech_gold_standard/new.csv saspeech_gold_standard/metadata.csv # keep only 1/4 of the dataset (1/1.5 hour)

python3 scripts/split_saspeech.py saspeech_gold_standard saspeech 10
```

_Build hebrew phonemizer rules_

```console
git clone https://github.com/thewh1teagle/espeak-ng -b he-patch-1
cd espeak-ng
cmake -B build .
cmake --build build
export ESPEAK_DATA_PATH=$(pwd)/build/espeak-ng-data
echo 'ESPEAK_DATA_PATH=$(pwd)/build/espeak-ng-data' >> ~/.bashrc
ls $ESPEAK_DATA_PATH
cd ..
```

_Fix pytorch erros to load models__

```console
rye add torchaudio==2.3.1
rye sync
```

```console
wget https://github.com/thewh1teagle/optispeech/releases/download/v0.1.0/espeak-ng-data.7z
7z x espeak-ng-data.7z
echo "export ESPEAK_DATA_PATH=$(pwd)/espeak-ng-data" >> ~/.bashrc
. ~/.bashrc
ls $ESPEAK_DATA_PATH
```


_Prepare dataset_

```console
python3 -m optispeech.tools.preprocess_dataset saspeech-he ./saspeech data/saspeech
```

_Generate statistics_

```console
python -m optispeech.tools.generate_data_statistics saspeech-he
```

_Start training_

```console
python -m optispeech.train \
    experiment="saspeech-he" \
    model.train_args.evaluate_utmos=false \
    data.batch_size=8 \
    data.num_workers=8 \
    data.train_filelist_path="data/saspeech/train.txt" \
    data.valid_filelist_path="data/saspeech/val.txt" \
    paths.log_dir="data/saspeech/logs" \
    callbacks.model_checkpoint.every_n_epochs=1  \
    callbacks.model_checkpoint.save_last=True \
    ckpt_path="last.ckpt"
```

# Setup rclone to copy to drive

```console
sudo apt install -y rclone
rclone config
> n
> gdrive
> 13
> y
> 'drive' in type
```

```console
tar -czvf saspeech.tar.gz data
7z a saspeech.7z data
rclone copy data/ gdrive:data -P
rclone copy gdrive:data data/ -P
rclone ls gdrive:
```

# Upload to github release

```console
gh release upload v0.1.0 saspeech.7z -R https://github.com/thewh1teagle/optispeech
wget https://github.com/thewh1teagle/optispeech/releases/download/v0.1.0/saspeech.7z
rm -rf data
tar xf saspeech.tar.gz
7z x saspeech.7z
```

# todo

```console
processing:  35%|██████████████████████████████████████████████████████████████████████████████████████████████████████████                                                                                                                                                                                                      | 104/298 [00:34<01:17,  2.50utterance/s]
ERROR 2024/09/08 10:34:31:  Failed to process item gold_000_line_104. Error: Failed to process file: gold_000_line_104.wav.
Caused by: Traceback (most recent call last):
  File "/root/home/optispeech/optispeech/tools/preprocess_dataset.py", line 42, in process_row
    data = do_preprocess_utterance(
  File "/root/home/optispeech/optispeech/dataset/text_wav_datamodule.py", line 35, in do_preprocess_utterance
    wav, mel, energy, pitch = feature_extractor(audio_filepath)
  File "/root/home/optispeech/optispeech/dataset/feature_extractors/__init__.py", line 95, in __call__
    pitch = self.get_pitch(wav, mel_length)
  File "/root/home/optispeech/optispeech/dataset/feature_extractors/__init__.py", line 137, in get_pitch
    return self.pitch_extractor(wav, mel_length)
  File "/root/home/optispeech/optispeech/dataset/feature_extractors/pitch_extractors.py", line 241, in __call__
    ptch = extractor(wav, mel_length)
  File "/root/home/optispeech/optispeech/dataset/feature_extractors/pitch_extractors.py", line 79, in __call__
    pitch = self.perform_interpolation(pitch)
  File "/root/home/optispeech/optispeech/dataset/feature_extractors/pitch_extractors.py", line 57, in perform_interpolation
    fill_value=(pitch[nonzero_ids[0]], pitch[nonzero_ids[-1]]),
IndexError: index 0 is out of bounds for axis 0 with size 0

```

## Export onnx

```console
python3 -m optispeech.onnx.export last.ckpt last.onnx
```

## Upload

```console
python3 -m optispeech.onnx.export last.ckpt last.onnx
7z a last.ckpt.7z last.ckpt
7z a last.onnx.7z last.onnx
gh release upload v0.1.0 last.ckpt.7z -R https://github.com/thewh1teagle/optispeech
gh release upload v0.1.0 last.onnx.7z -R https://github.com/thewh1teagle/optispeech
```