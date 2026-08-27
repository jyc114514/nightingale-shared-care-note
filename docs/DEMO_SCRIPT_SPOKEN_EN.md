# Nightingale spoken English demo script

Target runtime: approximately 3 minutes 30 seconds. Keep the UI in English. Use the local
fixture provider. Every record and audio file is synthetic. Text in the patient record is never
translated by the application.

## 0:00-0:20 - Opening

**Say:** “Nightingale is a shared-care note. It is not an autonomous medical system. It shows
what needs attention, and keeps every suggestion linked to an immutable source.”

**Action:** Open the local demo and sign in as the synthetic clinician.

**Pause:** Wait for the patient workspace and the Top Card.

## 0:20-1:05 - Glance and provenance

**Say:** “The Top Card has at most six items. Each item shows content, action, status, risk, and
source. Ranking priority is not a medical risk score.”

**Action:** Expand “Why ranked?”. Open a doctor-consult source.

**Say:** “This quote comes from a saved immutable version. I can check the exact span in the
timeline. The source stays visible after the focus animation.”

**Action:** Wait three seconds, refresh the deep link, then close the source.

**Say:** “Closing changes only the view. The patient query stays, and the highlight query is
removed.”

## 1:05-2:00 - Collaboration, history, and conflict

**Action:** Sign in as synthetic staff. Edit the staff note, open History, compare two versions,
and revert.

**Say:** “A revert creates a new snapshot. It never erases the old version.”

**Action:** Open Comments. Type at sign, choose a collaborator with the keyboard, add a root
comment, and add a reply. Assign a task from the comment and mark it done.

**Say:** “Comments are threaded. The task keeps its source comment and assignee. When the task is
open, it appears as a Glance action.”

**Action:** Use two browser windows if available. Show the second window receiving a metadata-only
update, then trigger two writes from one expected version.

**Say:** “The stale write returns four-oh-nine. The attempted content is preserved for review.
There is no silent last-write-wins.”

## 2:00-2:35 - Longitudinal context and privacy

**Action:** Open Historical context. Show Hot, Warm, and the derived cold summary. Open one
labelled original record.

**Say:** “The derived summary is not the original record. The immutable original remains the
source of truth.”

**Action:** Sign in as the synthetic patient.

**Say:** “The patient sees patient-facing summaries and instructions only. Internal comments,
tasks, raw AI notes, and conflict details are denied by the server.”

## 2:35-3:00 - Optional DeepSeek

**Action:** Return to a staff or clinician view. Open AI Scribe Demo. Keep the fixture selected.

**Say:** “The fixture is the default, so this demo does not need the network. DeepSeek is an
optional redacted adapter. It receives synthetic text only, and a provider failure never becomes
a fake fixture success.”

## 3:00-3:25 - Optional Voice, Level C

**Action:** Open Ambient Voice Prototype and select the synthetic nurse follow-up. Play the
pre-recorded audio, process it, and click a transcript segment.

**Say:** “This is a Level-C architecture and demo path. The audio is prerecorded synthetic signal
data. The transcript is a mock fixture because local ASR was not available in this environment.
Timestamps are fixture timestamps, and confidence is unavailable.”

**Action:** Show the generated suggestion source if present.

**Say:** “The suggestion remains system-authored and requires clinician review. There is no
microphone button.”

## 3:25-3:40 - Honest boundary

**Say:** “The prototype still needs an independent ten-second usability test and hosted deployment
security evidence. Render is configured for fixture AI and the Level-C Voice fixture. This prototype does not
claim clinical validation, production PHI capture, or model quality.”

**Action:** End on the English workspace and do not open credentials or configuration files.
