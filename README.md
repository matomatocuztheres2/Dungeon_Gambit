# Dungeon_Gambit
Dungeon Gambit is a high-stakes, pick-up-and-play Pygame deck-builder and dungeon-crawler that doubles as a unique story generator.
 In this game, every run is a new narrative, starting with basic stats and a randomized 20-card themed deck. 
 Players must draw cards, manage consumable equipment for temporary defense, and strategically use hard-earned XP for powerful, run-specific Level Ups to survive.
 With a simple, mobile-friendly UI and a progressive difficulty curve where newly added monsters grow stronger.
 This game creates a new, self-contained heroic tale of triumph or defeat in every addictive, quick-fire session.

 Why this game?
 This game is being developed as part of a larger project I have wanted to do.
 In this other project, this many game would be a source of gambling for the player.
 The cards would serve as collectibles, tradeable rewards, and incom for a lucky player.
 For you it will serves as a quick and easy pop-up Dungeon Crawler, and story generator.

 #--->How to Install: <---#
 
 *****Before anything else****
 You can probably skip this if you are part of the hackathon, but just to be safe.

 System Requirements:
* **Operating System:** Windows 10/11, macOS, or Linux (Ubuntu/Debian recommended for Linux users)
* **Python:** Version 3.8 or higher

**Install Python:**
    * If you don't have Python installed, download it from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/)
    * **IMPORTANT for Windows users:** During installation, make sure to check the box that says "Add Python to PATH" or "Add Python 3.x to PATH".

**Download the Game:**
    * Download and extract this game's `.zip` file to a folder on your computer (e.g., `DungeonsGambit/`).
    * https://github.com/matomatocuztheres2/Dungeon_Gambit

**Open Terminal/Command Prompt:**
    * **Windows:** Search for "cmd" or "PowerShell" in your Start menu.
    * **macOS/Linux:** Open your "Terminal" application.

**Navigate to the Game Folder:**
    * In your terminal/command prompt, use the `cd` command to go into the extracted game folder. For example, if you extracted it to your Desktop:
        ```bash
        cd Desktop/DungeonsGambit
        ```
        (Adjust the path to where you extracted it)

**Install Game Dependencies:**
    * Once inside the game folder, run the following command to install Pygame and any other required Python libraries:
        ```bash
        pip install -r requirements.txt
        ```

*****Assuming you are part of the hackathon and have all this done*****

 **1. Run the followng: pip install -r requirements.txt 
    - This ensures you have pygame, as well as the audio drivers needed to play this game
 **2. This game comes with music and audio. Please ensure you have libsdl2-mixer-2.0-0 or another audio driver available (See troubleshooting)

### Troubleshooting (Crucial for Linux/WSL Users)

* **`pygame.error: dsp: No such audio device` or other errors when running `python main.py` on Linux/WSL:**
    This indicates that some underlying system libraries required by Pygame for audio (or other features) are missing. You'll need to install them using your system's package manager.
    * **For Ubuntu/Debian-based systems (like your WSL Ubuntu):**
        ```bash
        sudo apt update
        sudo apt install libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-ttf-2.0-0 libsdl2-2.0-0
        # If specifically for MP3 audio and the above isn't enough:
        # sudo apt install libmpg123-0
        ```
        After running these commands, try running the game again with `python main.py`.
    * **(Add instructions for other Linux distros if you expect them, e.g., Fedora/Arch)**

* **"command not found: python" or "command not found: pip":** Make sure Python is installed and added to your system's PATH. Restart your terminal.
