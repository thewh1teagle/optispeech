from pathlib import Path
import librosa
import csv

metadata = 'saspeech_gold_standard/metadata.csv'
wavs = Path('saspeech_gold_standard/wavs')

with open(metadata, 'r', newline='') as f:
    reader = csv.reader(f, delimiter='|')
    rows = [row for row in reader]

new_rows = []
for row in rows:
    path = wavs / f'{row[0]}.wav'
    duration = librosa.get_duration(filename=str(path))
    if duration < 10:
        new_rows.append(row)

with open('saspeech_gold_standard/metadata_new.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter='|')
    writer.writerows(new_rows)
