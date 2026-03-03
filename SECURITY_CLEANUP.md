# Security Audit Note

This repository contains a GitHub Actions workflow (`reel_video_generator.yml`) that references `PEXELS_API_KEY` as a repository secret.

**SECURITY ACTION REQUIRED:**
The PEXELS_API_KEY stored in this repo's Actions Secrets was previously exposed in conversation logs and must be deleted from GitHub Settings > Secrets and variables > Actions.

Steps:
1. Go to https://github.com/mobiassistantv1-sys/Salford-reel-generator/settings/secrets/actions
2. Delete `PEXELS_API_KEY`
3. Also check for and delete `GEMINI_API_KEY` or `GOOGLE_API_KEY` if present
4. After revoking the key on Pexels, set a new key here if needed

Date: 2026-03-03 | Audit by: Winnie (Nebula IT)