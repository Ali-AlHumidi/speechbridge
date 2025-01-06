# **SpeechBridge**

The **SpeechBridge** Real-Time Language Translation App is a Python-based program that processes spoken language in real time to provide smooth multilingual communication.

The application converts live audio into text, translates it into a target language, then outputs the translation as synthetic voice using Google Cloud Voice-to-Text, Translation, and Text-to-Speech APIs. It incorporates these APIs into a streamlined workflow, enabling real-time speech-to-speech translation, and was designed with performance and low latency in mind.

The application exhibits sophisticated cloud technology integration with effective audio processing and supports a number of languages.

---

## **Setup Instructions**

### **1. Download and Install Required Applications**

#### **Install Docker**
1. Go to the [Docker Desktop Download](https://www.docker.com/products/docker-desktop).
2. Click **Download for Mac** and follow the installation instructions.
3. Open Docker Desktop and ensure it’s running (you should see the Docker logo in the menu bar).

#### **Install BlackHole**
1. BlackHole is a virtual audio driver required to route audio.
2. Visit the [BlackHole GitHub page](https://github.com/ExistentialAudio/BlackHole).
3. Download and install **BlackHole 2ch**.
4. Follow the installation steps. When prompted, allow system extensions.


---

### **2. Configure BlackHole**

#### **Open Audio MIDI Setup**
1. Press `Command + Space` and type **Audio MIDI Setup**, then press `Enter`.
2. In the **Audio MIDI Setup** window, click the `+` button in the bottom-left corner and select **Create Multi-Output Device**.

---

#### **Add Devices to Multi-Output**
1. In the list of audio devices, check:
   - **BlackHole 2ch**
   - **MacBook Pro Speakers** (or your system's primary speakers)
2. Set **BlackHole 2ch** as the Primary Device.

#### **Set System Output to BlackHole**
1. Go to `System Preferences > Sound`.
2. Under the **Output** tab, select **Multi-Output Device**.

#### **Set BlackHole as the Input Device**
1. Under the **Input** tab in the same settings, select **BlackHole 2ch**.

---

### **3. Download the SpeechBridge App**

#### **Clone or Download the Repository**

1. Clone the app repository using Git:
   ```bash
   git clone https://github.com/Ali-AlHumidi/speechbridge.git
   Alternatively, download the repository as a ZIP file from GitHub and extract it.   '

### **4. Download Google Cloud Credentials**
1. Set up a Google Cloud service account and download the JSON credentials file.
2. Save the file as `credentials.json` in a safe location.

---

### **5. Build and Run the App Using Docker**

#### **Open Terminal**
1. Press `Command + Space`, type `Terminal`, and press Enter.

#### **Navigate to the App Directory**
1. Use the `cd` command to navigate to the folder where you saved the app:
   ```bash
   cd /path/to/speechbridge

Replace /path/to/speechbridge with the actual path to the folder.

#### **Build the Docker Image**

1. Run the following command to create the app image:

docker build -t speechbridge .

#### **Run the App in Docker**

1. Run the following command to start the app:
docker run -it --rm \
-v /path/to/credentials.json:/app/credentials.json \
-e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
speechbridge

Replace /path/to/credentials.json with the actual path to your credentials.json file.

---

### **6. Using the App**

#### **Open the GUI**
- The app will launch with a simple interface.

#### **Select Target Language**
- Use the dropdown menu to select the language you want to translate into.

#### **Click Start**
- Begin speaking into your microphone.
- The app will transcribe, translate, and output the translated speech as audio.

#### **Click Stop**
- Stop the translation process.

---
---

### **7. Notes**

- **BlackHole Installation**:  
  BlackHole is required for the app to work properly. Ensure it is installed and configured as per the instructions above.

- **Google Cloud Credentials**:  
  Ensure you have valid Google Cloud credentials (the `credentials.json` file) and that they are correctly mapped in the Docker `run` command.

- **Docker Requirements**:  
  Make sure Docker is installed and running on your system before attempting to build or run the app.

- **Audio Configuration**:  
  Double-check your audio configuration to ensure that:
  - **Multi-Output Device** is set up properly.
  - **BlackHole** is selected as the Input Device in your system sound settings.

- **Debugging Tips**:  
  If you encounter any errors:
  1. Check the logs in the terminal for specific issues.
  2. Ensure all dependencies are installed as mentioned in the setup steps.
  3. Verify that Docker has access to the correct credentials file path.

Feel free to reach out or open an issue on the GitHub repository if you encounter any problems.

---


