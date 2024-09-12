"""
Split dataset that has the following structure:
dataset/
    wavs/
    metadata.csv
Into new structure:
new_dataset/
    train/
        wav/
        metadata.csv
    val/
        wav/
        metadata.csv
"""
import shutil
import sys
from pathlib import Path
import csv

input = Path(sys.argv[1])
output = Path(sys.argv[2])
VALIDATION_PERCENT = int(sys.argv[3]) # integer as percent

input_wav_path = input / 'wavs'
input_metadata_csv = input / 'metadata.csv'

train_output = output / 'train'
validation_output = output / 'val'

train_wav_path = train_output / 'wav'
train_metadata_csv = train_output / 'metadata.csv'

validation_wav_path = validation_output / 'wav'
validation_metadata_csv = validation_output / 'metadata.csv'

# Create output directories
train_output.mkdir(parents=True, exist_ok=True)
validation_output.mkdir(parents=True, exist_ok=True)
train_wav_path.mkdir(parents=True, exist_ok=True)
validation_wav_path.mkdir(parents=True, exist_ok=True)

# Read metadata
with open(input_metadata_csv, 'r', encoding='utf-8') as metadata_file:
    metadata = list(csv.reader(metadata_file, delimiter='|'))

# Calculate split index for validation
validation_split_idx = int(len(metadata) * (VALIDATION_PERCENT / 100))

# Split dataset
validation_data = metadata[:validation_split_idx]
train_data = metadata[validation_split_idx:]

# Write training metadata
with open(train_metadata_csv, 'w', encoding='utf-8', newline='') as train_metadata_file:
    writer = csv.writer(train_metadata_file, delimiter='|')
    train_data = [[i[0], i[1]] for i in train_data]
    writer.writerows(train_data)

# Write validation metadata
with open(validation_metadata_csv, 'w', encoding='utf-8', newline='') as validation_metadata_file:
    writer = csv.writer(validation_metadata_file, delimiter='|')
    validation_data = [[i[0], i[1]] for i in validation_data]
    writer.writerows(validation_data)

# Copy wav files for training data
for file_id, _, in train_data:
    src_wav = input_wav_path / f"{file_id}.wav"
    dst_wav = train_wav_path / f"{file_id}.wav"
    shutil.copyfile(src_wav, dst_wav)

# Copy wav files for validation data
for file_id, _, in validation_data:
    src_wav = input_wav_path / f"{file_id}.wav"
    dst_wav = validation_wav_path / f"{file_id}.wav"
    shutil.copyfile(src_wav, dst_wav)