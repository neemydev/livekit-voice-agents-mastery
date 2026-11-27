"""The ears (STT) know the clinic's name and the doctors' names, so Deepgram spells them right.

Specs: specs/dental_receptionist/002-session-events/  (keyterm prompting)
       specs/dental_receptionist/004-instructions-and-facts/  (the doctors' names)

No network: making the STT object doesn't call Deepgram. The plugin checks that a key
exists, so we set a fake one if the real one is missing.
"""

import os

from dental_receptionist.agent import build_stt


def test_stt_knows_clinic_name(monkeypatch) -> None:
    if not os.getenv("DEEPGRAM_API_KEY"):
        monkeypatch.setenv("DEEPGRAM_API_KEY", "fake-key-for-this-test")

    stt = build_stt()

    # "_opts" is the plugin's private settings box. Reading it is fine for a learning project;
    # if LiveKit ever renames it, this test fails and tells us.
    for term in ["Bright Smile Dental", "Dr. Chen", "Dr. Park"]:
        assert term in stt._opts.keyterm, f"the ears don't know {term!r}"
