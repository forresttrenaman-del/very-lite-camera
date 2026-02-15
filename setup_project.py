#!/usr/bin/env python3
"""
Very Lite Camera - Single File Installer
Upload this ONE file to GitHub and run it to extract the entire project.

Usage:
1. Upload this file to your GitHub repository
2. In GitHub Actions, it will run automatically
   OR
3. Download and run locally: python3 setup_project.py
"""

import os
import base64
import sys

def create_directory(path):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)
    print(f"✓ Created directory: {path}")

def write_file(path, content, is_binary=False):
    """Write content to file"""
    create_directory(os.path.dirname(path))
    mode = 'wb' if is_binary else 'w'
    with open(path, mode) as f:
        f.write(content)
    print(f"✓ Created file: {path}")

def make_executable(path):
    """Make file executable (for gradlew)"""
    if os.path.exists(path):
        os.chmod(path, 0o755)
        print(f"✓ Made executable: {path}")

print("=" * 60)
print("Very Lite Camera - Project Setup")
print("=" * 60)
print()

# Create all project files
files = {
    ".github/workflows/build-apk.yml": """name: Build Android APK

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
        cache: gradle
    
    - name: Setup project
      run: python3 setup_project.py
    
    - name: Grant execute permission for gradlew
      run: chmod +x gradlew
    
    - name: Build debug APK
      run: ./gradlew assembleDebug --stacktrace
    
    - name: Upload Debug APK
      uses: actions/upload-artifact@v4
      with:
        name: very-lite-camera-debug
        path: app/build/outputs/apk/debug/app-debug.apk
        retention-days: 30
    
    - name: Create Release
      if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
      uses: softprops/action-gh-release@v1
      with:
        tag_name: v1.0-${{ github.run_number }}
        name: Very Lite Camera v1.0-${{ github.run_number }}
        body: |
          Download the APK below and install on your Android device.
        files: |
          app/build/outputs/apk/debug/app-debug.apk
        draft: false
        prerelease: false
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      continue-on-error: true
""",

    "settings.gradle": """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "Very Lite Camera"
include ':app'
""",

    "gradle.properties": """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
""",

    "build.gradle": """plugins {
    id 'com.android.application' version '8.2.0' apply false
    id 'com.android.library' version '8.2.0' apply false
    id 'org.jetbrains.kotlin.android' version '1.9.20' apply false
}
""",

    "gradle/wrapper/gradle-wrapper.properties": """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.2-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""",

    ".gitignore": """*.apk
*.ap_
*.aab
*.dex
*.class
bin/
gen/
out/
release/
.gradle/
build/
local.properties
proguard/
*.log
.navigation/
captures/
*.iml
.idea/
*.ipr
*.iws
*.jks
*.keystore
.externalNativeBuild
google-services.json
.DS_Store
*.hprof
""",

    "app/build.gradle": """plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.lowquality.videorecorder'
    compileSdk 34

    defaultConfig {
        applicationId "com.lowquality.videorecorder"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
    
    kotlinOptions {
        jvmTarget = '1.8'
    }
    
    buildFeatures {
        viewBinding true
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}
""",

    "app/src/main/res/values/strings.xml": """<resources>
    <string name="app_name">Very Lite Camera</string>
</resources>
""",

    "app/src/main/res/drawable/button_background.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#4CAF50" />
    <corners android:radius="12dp" />
</shape>
""",

    "app/src/main/res/drawable/recording_indicator.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="#FF0000" />
</shape>
""",
}

# Write all text files
for filepath, content in files.items():
    write_file(filepath, content)

# Now create the large files (Kotlin source and XML layouts)
print("\nCreating source code files...")

# MainActivity.kt
mainactivity_kt = """package com.lowquality.videorecorder

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.lowquality.videorecorder.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private var isRecording = false
    
    companion object {
        private const val REQUEST_CODE_PERMISSIONS = 10
        private val REQUIRED_PERMISSIONS = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.READ_EXTERNAL_STORAGE
        )
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        if (allPermissionsGranted()) {
            setupUI()
        } else {
            ActivityCompat.requestPermissions(
                this, REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS
            )
        }
    }

    private fun setupUI() {
        updateRecordingStatus(false)
        
        binding.btnRecord.setOnClickListener {
            if (isRecording) {
                stopRecording()
            } else {
                startRecording()
            }
        }

        binding.btnSettings.setOnClickListener {
            Toast.makeText(this, "Settings: 480p @ 1.5 Mbps", Toast.LENGTH_SHORT).show()
        }
    }

    private fun startRecording() {
        val intent = Intent(this, RecordingService::class.java)
        intent.action = RecordingService.ACTION_START_RECORDING
        ContextCompat.startForegroundService(this, intent)
        
        isRecording = true
        updateRecordingStatus(true)
        Toast.makeText(this, "Recording started", Toast.LENGTH_SHORT).show()
    }

    private fun stopRecording() {
        val intent = Intent(this, RecordingService::class.java)
        intent.action = RecordingService.ACTION_STOP_RECORDING
        startService(intent)
        
        isRecording = false
        updateRecordingStatus(false)
        Toast.makeText(this, "Recording stopped", Toast.LENGTH_SHORT).show()
    }

    private fun updateRecordingStatus(recording: Boolean) {
        if (recording) {
            binding.btnRecord.text = "⏹ Stop Recording"
            binding.btnRecord.setBackgroundColor(getColor(android.R.color.holo_red_dark))
            binding.tvStatus.text = "Recording..."
            binding.tvStatus.setTextColor(getColor(android.R.color.holo_red_dark))
            binding.recordingIndicator.visibility = android.view.View.VISIBLE
        } else {
            binding.btnRecord.text = "⏺ Start Recording"
            binding.btnRecord.setBackgroundColor(getColor(android.R.color.holo_green_dark))
            binding.tvStatus.text = "Ready to record"
            binding.tvStatus.setTextColor(getColor(android.R.color.darker_gray))
            binding.recordingIndicator.visibility = android.view.View.GONE
        }
    }

    private fun allPermissionsGranted() = REQUIRED_PERMISSIONS.all {
        ContextCompat.checkSelfPermission(baseContext, it) == PackageManager.PERMISSION_GRANTED
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_CODE_PERMISSIONS) {
            if (allPermissionsGranted()) {
                setupUI()
            } else {
                Toast.makeText(
                    this,
                    "Permissions required",
                    Toast.LENGTH_LONG
                ).show()
                finish()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (isRecording) {
            stopRecording()
        }
    }
}
"""
write_file("app/src/main/java/com/lowquality/videorecorder/MainActivity.kt", mainactivity_kt)

# RecordingService.kt - Split into parts due to length
recordingservice_pt1 = """package com.lowquality.videorecorder

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.media.AudioManager
import android.media.MediaRecorder
import android.media.ToneGenerator
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.util.Log
import androidx.core.app.NotificationCompat
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

class RecordingService : Service() {

    private var mediaRecorder: MediaRecorder? = null
    private var toneGenerator: ToneGenerator? = null
    private val handler = Handler(Looper.getMainLooper())
    private var beepRunnable: Runnable? = null
    private var isRecording = false
    private var outputFile: File? = null

    companion object {
        const val ACTION_START_RECORDING = "com.lowquality.videorecorder.START_RECORDING"
        const val ACTION_STOP_RECORDING = "com.lowquality.videorecorder.STOP_RECORDING"
        private const val NOTIFICATION_ID = 1
        private const val CHANNEL_ID = "recording_channel"
        private const val TAG = "RecordingService"
        private const val BEEP_INTERVAL_MS = 30000L
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        toneGenerator = ToneGenerator(AudioManager.STREAM_NOTIFICATION, 100)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START_RECORDING -> {
                if (!isRecording) {
                    startRecording()
                }
            }
            ACTION_STOP_RECORDING -> {
                stopRecording()
                stopSelf()
            }
        }
        return START_STICKY
    }

    private fun startRecording() {
        try {
            val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
            val videoDir = File(getExternalFilesDir(null), "Videos")
            if (!videoDir.exists()) {
                videoDir.mkdirs()
            }
            outputFile = File(videoDir, "VID_$timestamp.mp4")

            mediaRecorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                MediaRecorder(this)
            } else {
                @Suppress("DEPRECATION")
                MediaRecorder()
            }

            mediaRecorder?.apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setVideoSource(MediaRecorder.VideoSource.SURFACE)
                setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                setOutputFile(outputFile?.absolutePath)
                setVideoEncoder(MediaRecorder.VideoEncoder.H264)
                setVideoSize(640, 480)
                setVideoFrameRate(24)
                setVideoEncodingBitRate(1_500_000)
                setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                setAudioEncodingBitRate(64_000)
                setAudioSamplingRate(22050)
                prepare()
                start()
            }

            isRecording = true
            startBeepTimer()
            startForeground(NOTIFICATION_ID, createNotification("Recording..."))
            
            Log.d(TAG, "Recording started")
            
        } catch (e: Exception) {
            Log.e(TAG, "Error starting recording", e)
            stopRecording()
        }
    }

    private fun stopRecording() {
        try {
            stopBeepTimer()
            mediaRecorder?.apply {
                stop()
                reset()
                release()
            }
            mediaRecorder = null
            isRecording = false
            Log.d(TAG, "Recording stopped")
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping recording", e)
        }
    }

    private fun startBeepTimer() {
        beepRunnable = object : Runnable {
            override fun run() {
                playBeep()
                handler.postDelayed(this, BEEP_INTERVAL_MS)
            }
        }
        handler.postDelayed(beepRunnable!!, BEEP_INTERVAL_MS)
    }

    private fun stopBeepTimer() {
        beepRunnable?.let {
            handler.removeCallbacks(it)
        }
        beepRunnable = null
    }

    private fun playBeep() {
        toneGenerator?.startTone(ToneGenerator.TONE_PROP_BEEP, 200)
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Recording Service",
                NotificationManager.IMPORTANCE_LOW
            )
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(text: String) = NotificationCompat.Builder(this, CHANNEL_ID)
        .setContentTitle("Very Lite Camera")
        .setContentText(text)
        .setSmallIcon(android.R.drawable.ic_menu_camera)
        .setOngoing(true)
        .setContentIntent(
            PendingIntent.getActivity(
                this,
                0,
                Intent(this, MainActivity::class.java),
                PendingIntent.FLAG_IMMUTABLE
            )
        )
        .build()

    override fun onDestroy() {
        super.onDestroy()
        stopRecording()
        toneGenerator?.release()
        toneGenerator = null
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
"""
write_file("app/src/main/java/com/lowquality/videorecorder/RecordingService.kt", recordingservice_pt1)

# AndroidManifest.xml
manifest_xml = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.lowquality.videorecorder">

    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />

    <uses-feature android:name="android.hardware.camera" android:required="true" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.VideoRecorder">
        
        <activity
            android:name=".MainActivity"
            android:screenOrientation="portrait"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".RecordingService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="camera" />
    </application>

</manifest>
"""
write_file("app/src/main/AndroidManifest.xml", manifest_xml)

# activity_main.xml - the layout file
print("\nNote: activity_main.xml is complex. Creating simplified version...")
print("For full UI, you may need to create it separately or use Android Studio.")

activity_main_xml = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp"
    android:background="#1a1a1a"
    android:gravity="center">

    <TextView
        android:id="@+id/tvAppTitle"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Very Lite Camera"
        android:textSize="24sp"
        android:textColor="#ffffff"
        android:textStyle="bold"
        android:layout_marginBottom="16dp" />

    <View
        android:id="@+id/recordingIndicator"
        android:layout_width="16dp"
        android:layout_height="16dp"
        android:background="@drawable/recording_indicator"
        android:visibility="gone"
        android:layout_marginBottom="8dp" />

    <TextView
        android:id="@+id/tvStatus"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Ready to record"
        android:textSize="18sp"
        android:textColor="#808080"
        android:layout_marginBottom="32dp" />

    <Button
        android:id="@+id/btnRecord"
        android:layout_width="match_parent"
        android:layout_height="64dp"
        android:text="⏺ Start Recording"
        android:textSize="18sp"
        android:background="@drawable/button_background"
        android:layout_marginBottom="16dp" />

    <Button
        android:id="@+id/btnSettings"
        android:layout_width="match_parent"
        android:layout_height="48dp"
        android:text="⚙ Settings"
        android:textSize="16sp" />

</LinearLayout>
"""
write_file("app/src/main/res/layout/activity_main.xml", activity_main_xml)

# Create gradlew script
print("\nCreating Gradle wrapper...")
gradlew_content = """#!/bin/sh
# Gradle wrapper script
GRADLE_WRAPPER_JAR="gradle/wrapper/gradle-wrapper.jar"
if [ ! -f "$GRADLE_WRAPPER_JAR" ]; then
    echo "Downloading Gradle wrapper..."
    mkdir -p gradle/wrapper
    wget -O "$GRADLE_WRAPPER_JAR" "https://github.com/gradle/gradle/raw/master/gradle/wrapper/gradle-wrapper.jar" 2>/dev/null || \\
    curl -o "$GRADLE_WRAPPER_JAR" "https://github.com/gradle/gradle/raw/master/gradle/wrapper/gradle-wrapper.jar"
fi
java -jar "$GRADLE_WRAPPER_JAR" "$@"
"""
write_file("gradlew", gradlew_content)
make_executable("gradlew")

# Create gradlew.bat for Windows
gradlew_bat = """@echo off
java -jar gradle\\wrapper\\gradle-wrapper.jar %*
"""
write_file("gradlew.bat", gradlew_bat)

# Create README
readme = """# Very Lite Camera

A lightweight Android video recorder app.

## Building

This project uses GitHub Actions to automatically build APKs.

1. Push this code to GitHub
2. GitHub Actions will build the APK automatically
3. Download from the Actions tab → Artifacts

## Local Building

```bash
./gradlew assembleDebug
```

APK will be in: `app/build/outputs/apk/debug/app-debug.apk`
"""
write_file("README.md", readme)

print("\n" + "=" * 60)
print("✅ PROJECT SETUP COMPLETE!")
print("=" * 60)
print("\nAll files and folders have been created.")
print("\nNext steps:")
print("1. Commit these files to Git")
print("2. Push to GitHub")
print("3. GitHub Actions will build your APK automatically!")
print("\nOr build locally with: ./gradlew assembleDebug")
print()
