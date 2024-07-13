import argparse
from hashlib import md5
from pathlib import Path
from time import perf_counter

import numpy as np
import torch
import soundfile as sf
from torch.nn.utils.rnn import pad_sequence, unpad_sequence

from optispeech.model import OptiSpeech
from optispeech.utils import pylogger


log = pylogger.get_pylogger(__name__)


def main():
    parser = argparse.ArgumentParser(description=" Speaking text using OptiSpeech")

    parser.add_argument(
        "checkpoint",
        type=str,
        help="Path to OptiSpeech checkpoint",
    )
    parser.add_argument("text", type=str, help="Text to synthesise")
    parser.add_argument(
        "output_dir",
        type=str,
        help="Directory to write generated audio  to.",
    )
    parser.add_argument("--d-factor", type=float, default=1.0, help="Scale to control speech rate")
    parser.add_argument("--p-factor", type=float, default=1.0, help="Scale to control pitch")
    parser.add_argument("--e-factor", type=float, default=1.0, help="Scale to control energy")
    parser.add_argument("--cuda", action="store_true", help="Use GPU for inference")

    args = parser.parse_args()

    device = torch.device("cuda") if args.cuda else torch.device("cpu")
    model = OptiSpeech.load_from_checkpoint(args.checkpoint, map_location="cpu")
    model.to(device)
    model.eval()

    x, x_lengths, clean_text = model.prepare_input(args.text)
    log.info(f"Cleaned text: {clean_text}")

    synth_outs = model.synthesise(
        x=x,
        x_lengths=x_lengths,
        d_factor=args.d_factor,
        p_factor=args.p_factor,
        e_factor=args.e_factor,
    )
    wavs = synth_outs["wav"]
    wav_lengths = synth_outs["wav_lengths"]
    print(f"RTF: {synth_outs['rtf']}")
    print(f"Latency: {synth_outs['latency']}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for (i, wav) in enumerate(unpad_sequence(wavs, wav_lengths, batch_first=True)):
        outfile = output_dir.joinpath(f"gen-{i + 1}")
        out_wav = outfile.with_suffix(".wav")
        wav = wav.squeeze().float().detach().cpu().numpy()
        sf.write(out_wav, wav, model.sample_rate)
        log.info(f"Wrote audio to {out_wav}")


if __name__ == "__main__":
    main()
