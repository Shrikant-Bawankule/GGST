step 01:

clone the repo

step 02 :

create a data folder with raw audio with transcript each seperate folder.
And create folders for clean audio, hypothesis and reference text (your raw transcript file)
and the add path accordingly in the code

step 03:

pip install -r requirments.txt -----> it install all needed libraries and models.

step 04:

And run main.py ------> it do preproceesing and transcribe and save in hypothesis.

from that you should have groud truth(raw transcript) and hypothesis(asr transcript)make sure there are same to same audio sample and transcript mismatch may affect evaluation

step 05:

And run evalaute.py------> it calculate the wer/cer/ser value
