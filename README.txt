Medical Transcriber Application
================================

QUICK START:
1. Set up Google Cloud credentials (see Prerequisites section below)
2. Double-click MedicalTranscriber.exe
3. Enter patient information and start recording

PREREQUISITES:
- Windows 10 or 11
- Google Cloud account with Speech-to-Text API enabled
- Microphone access
- Google Cloud service account credentials (JSON key file)

SETUP STEPS:

1. Google Cloud Credentials Setup:
   [INSTRUCTIONS TO BE FILLED IN]
   - How to create a service account
   - How to download the JSON key file
   - Where to store the key file (recommended: outside the application folder)

2. Environment Variable Setup:
   [INSTRUCTIONS TO BE FILLED IN]
   - How to set GOOGLE_APPLICATION_CREDENTIALS environment variable
   - Windows System Properties method
   - Or command line method

USAGE:

Basic Workflow:
1. Enter Patient Name and DOB (YYYYMMDD format)
2. Optionally select a template from the dropdown
3. Click "Record" to start recording
4. Click "Stop" when finished
5. Click "Send to Google" to transcribe
6. Review and edit the transcription in the editor
7. Click "Clean Transcription" to remove filler words (optional)
8. Click "Save" to save the transcription

File Management:
- Load existing transcriptions from the left panel file browser
- Click on a file name to load it into the editor
- Click "Delete Transcription" to securely delete a loaded file
- Click "Delete Recording" to securely delete the current audio recording

FOLDER STRUCTURE:
The application will create these folders automatically in the same directory as the executable:
- transcriptions/  (saved medical records - HIPAA retention applies)
- recordings/      (temporary audio files - securely deleted after transcription)
- audit_logs/      (HIPAA compliance logs - deletion and access audit trail)
- templates/       (template files for transcription formatting)

IMPORTANT NOTES:

Security & HIPAA Compliance:
- Keep your Google Cloud credentials secure - treat them as PHI-level security
- Transcriptions are saved locally - back them up regularly per your organization's policy
- Audio files are securely deleted after successful transcription (overwritten multiple times)
- All file deletions are logged in audit_logs/audit_log.csv for compliance monitoring
- Transcriptions in the transcriptions/ folder are the retained medical records
- Follow your organization's retention policy (typically 5-10 years per state law)

Troubleshooting:

- "Failed to execute script": Ensure the executable has proper permissions and is not blocked by antivirus
- Audio recording issues: Check microphone permissions in Windows Settings
- Google Cloud errors: Verify credentials are set correctly via environment variable
- Transcription fails: Check internet connection and Google Cloud API access
- File not found errors: Ensure the application has write permissions in its directory

For detailed Google Cloud setup instructions, see CREDENTIALS_SETUP.md (if provided)

SUPPORT:
[CONTACT INFORMATION TO BE FILLED IN]

VERSION:
1.0.0

