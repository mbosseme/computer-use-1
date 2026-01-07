# Troubleshooting Log: AppleScript PowerPoint Rendering

## Objective
To programmatically render slides from a `.pptx` file into `.png` images using the installed Microsoft PowerPoint (macOS) via AppleScript.

## Current Behavior
The AppleScript executes without throwing an error code, often logging "Success", but **no files appear on disk**.

## Methods Attempted

### 1. Simple Export (`save as PNG`)
**Script Logic:**
```applescript
save thePres in outputPosixFolder as save as PNG
```
**Outcome:** Script completes, but target folder remains empty.

### 2. Explicit `export` command
**Script Logic:**
```applescript
export thePres to outputPosixFolder as slide images with properties {height: 1080, width: 1920}
```
**Outcome:** Syntax error `-2741`; newer PowerPoint versions often drop support for the explicit `export` verb in favor of `save as`.

### 3. Iterative Slide Save
**Script Logic:**
```applescript
repeat with i from 1 to count of slides...
   save (slide i) in targetFile as list as PNG
```
**Outcome:** Parameter error `-50`. Saving individual slide objects is chemically unstable in recent versions.

### 4. Desktop / Pictures Folder Relay
**Script Logic:**
Target `~/Desktop` or `~/Pictures` explicitly to bypass assumed Sandbox restrictions.
**Outcome:** Script runs, claims success, but folders (`Agent_Render_Temp`) are either not created or empty.

## Hypotheses
1.  **Sandboxing:** PowerPoint is sandboxed and lacks the specific entitlement to write to the folders we are requesting, even standard ones like Desktop/Pictures, when driven by `osascript` (which itself might be restricted when called from VS Code's terminal).
2.  **Output Path Resolution:** The `in` parameter for `save` might be interpreted as a filename base rather than a folder, or vice-versa, causing it to write to a hidden temp location or fail silently.
3.  **Prompt Interference:** PowerPoint might be throwing a modal dialog ("Grant Access?") that is invisible or instantly dismissed/ignored by the script runner.

## Key Search Terms for You
*   "AppleScript Microsoft PowerPoint save as PNG no files"
*   "automating powerpoint macos sandboxing output folder"
*   "osascript powerpoint grant access to folder"
