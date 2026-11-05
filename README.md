# Text-to-speech service

`POST /synthesize` returns `audio/wav`. Junction forwards `/texttospeech/synthesize` to this route. Send `voice_type: "SIMPLE"` for a local Windows speech preset or `voice_type: "CLONE"` for the Pocket TTS reference recording. Omitting `voice_type` preserves the original clone behavior.

```json
{"text":"Hello from Relay.","voice_type":"SIMPLE","voice_name":"Microsoft Zira Desktop","pitch":3,"rate":0,"volume":100}
```

All SIMPLE controls are optional. The example shows their defaults. `voice_name` is the name of an installed Windows SAPI desktop voice. `pitch` and `rate` range from -10 to 10, and `volume` from 0 to 100. The preset works offline and requires the selected voice to be installed for the account running Junction. An unknown voice returns HTTP 422. SIMPLE works independently of Pocket TTS readiness. `/ready` continues to indicate clone readiness.

```json
{"text":"Hello from Relay.","voice_type":"CLONE"}
```
