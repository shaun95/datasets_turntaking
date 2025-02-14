from os.path import join, expanduser
from datasets import load_dataset
from datasets_turntaking.utils import repo_root


DATASET_SCRIPT = join(repo_root(), "datasets_turntaking/switchboard/switchboard.py")
AUDIO_DIR = join(expanduser("~"), "projects/data/switchboard/audio")
EXT = ".wav"


def load_switchboard(split="train", audio_root=AUDIO_DIR, ext=EXT):
    if split == "val":
        split = "validation"

    def process_and_add_name(examples):
        examples["dataset_name"] = "switchboard"
        if audio_root is not None:
            examples["audio_path"] = join(audio_root, examples["audio_path"] + ext)

        return examples

    dset = load_dataset(DATASET_SCRIPT, name="clean", split=split)
    # dset = dset.remove_columns(["speaker_id", "chapter_id"])
    dset = dset.map(process_and_add_name)
    return dset
